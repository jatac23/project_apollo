"""DEX user labeler for addresses that trade on decentralized exchanges."""

from typing import List
import logging
import pandas as pd

from .base_labeler import BaseLabeler
from ..models import AddressLabel

logger = logging.getLogger(__name__)


class DEXUserLabeler(BaseLabeler):
    """Labeler for identifying addresses that actively trade on DEXs."""

    def __init__(self, bq_client=None, min_interactions: int = 5):
        """Initialize DEX user labeler.

        Args:
            bq_client: BigQuery client instance
            min_interactions: Minimum DEX interactions required
        """
        super().__init__(bq_client)
        self.min_interactions = min_interactions
        self.label_type = 'dex_user'

    def _get_dex_users(self) -> pd.DataFrame:
        """Get addresses that have interacted with known DEX router contracts.
        
        Returns:
            pd.DataFrame: DataFrame with DEX user information
        """
        # Known DEX router contracts (simplified list)
        dex_contracts = [
            "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",  # Uniswap V2 Router
            "0xe592427a0aece92de3edee1f18e0157c05861564",  # Uniswap V3 Router
            "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506",  # SushiSwap Router
            "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f",  # SushiSwap Router V2
            "0x1111111254fb6c44bac0bed2854e76f90643097d",  # 1inch V4 Router
        ]

        contracts_str = "', '".join(dex_contracts)

        query = f"""
        SELECT DISTINCT
            from_address as address,
            COUNT(DISTINCT to_address) as unique_dex_contracts,
            COUNT(*) as total_dex_interactions,
            CURRENT_TIMESTAMP() as created_at,
            CURRENT_TIMESTAMP() as updated_at
        FROM `bigquery-public-data.crypto_ethereum.transactions`
        WHERE DATE(block_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        AND to_address IN ('{contracts_str}')
        GROUP BY from_address
        HAVING total_dex_interactions >= {self.min_interactions}
        ORDER BY total_dex_interactions DESC
        LIMIT 10000
        """
        return self.bq_client.execute_query(query)

    def generate_labels(self) -> List[AddressLabel]:
        """Generate DEX user labels for addresses with DEX activity.

        Returns:
            List[AddressLabel]: List of DEX user address labels
        """
        df = self._get_dex_users()

        labels = []
        for _, row in df.iterrows():
            # Calculate confidence based on number of unique DEX contracts and total interactions
            unique_contracts = row['unique_dex_contracts']
            total_interactions = row['total_dex_interactions']

            # Higher confidence for more diverse DEX usage and higher activity
            # Max score at 5+ unique DEXs
            contract_score = min(1.0, unique_contracts / 5.0)
            # Max score at 50+ interactions
            activity_score = min(1.0, total_interactions / 50.0)
            confidence = (contract_score + activity_score) / 2.0

            # Ensure minimum confidence
            confidence = max(0.25, confidence)

            label = AddressLabel(
                address=row['address'],
                label=self.label_type,
                confidence=confidence,
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                source_rule=f'dex_interactions >= {self.min_interactions}'
            )
            labels.append(label)

        return labels

    def get_min_interactions(self) -> int:
        """Get the minimum DEX interactions required for labeling."""
        return self.min_interactions

    def set_min_interactions(self, min_interactions: int):
        """Set the minimum DEX interactions required for labeling.

        Args:
            min_interactions: New minimum interaction threshold
        """
        self.min_interactions = min_interactions
        logger.info(
            f"Updated DEX user minimum interactions to {min_interactions}")

    def get_confidence_calculation_info(self) -> dict:
        """Get information about how confidence is calculated.

        Returns:
            dict: Confidence calculation parameters
        """
        return {
            'min_interactions': self.min_interactions,
            'contract_score_formula': 'min(1.0, unique_contracts / 5.0)',
            'activity_score_formula': 'min(1.0, total_interactions / 50.0)',
            'final_formula': '(contract_score + activity_score) / 2.0',
            'min_confidence': 0.25,
            'description': 'Confidence based on DEX diversity and activity level'
        }
