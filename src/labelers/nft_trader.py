"""NFT trader labeler for addresses with high NFT activity."""

from typing import List
import logging
import pandas as pd

from .base_labeler import BaseLabeler
from ..models import AddressLabel
from config import settings

logger = logging.getLogger(__name__)


class NFTTraderLabeler(BaseLabeler):
    """Labeler for identifying addresses with high NFT trading activity."""

    def __init__(self, bq_client=None, threshold: float = None, min_activity: int = 10):
        """Initialize NFT trader labeler.

        Args:
            bq_client: BigQuery client instance
            threshold: NFT interaction ratio threshold (defaults to config)
            min_activity: Minimum total interactions required
        """
        super().__init__(bq_client)
        self.threshold = threshold or settings.nft_trader_threshold
        self.min_activity = min_activity
        self.label_type = 'nft_trader'

    def _get_nft_traders(self) -> pd.DataFrame:
        """Get addresses with high percentage of ERC-721 interactions.
        
        Returns:
            pd.DataFrame: DataFrame with NFT trader information
        """
        query = f"""
        WITH address_interactions AS (
            SELECT 
                from_address as address,
                COUNT(*) as total_interactions,
                SUM(CASE WHEN token_address IN (
                    SELECT DISTINCT token_address 
                    FROM `bigquery-public-data.crypto_ethereum.token_transfers` 
                    WHERE token_address IS NOT NULL
                    LIMIT 1000
                ) THEN 1 ELSE 0 END) as nft_interactions
            FROM `bigquery-public-data.crypto_ethereum.token_transfers`
            WHERE DATE(block_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
            GROUP BY from_address
            HAVING total_interactions >= {self.min_activity}
        )
        SELECT 
            address,
            nft_interactions / total_interactions as nft_ratio,
            total_interactions,
            nft_interactions,
            CURRENT_TIMESTAMP() as created_at,
            CURRENT_TIMESTAMP() as updated_at
        FROM address_interactions
        WHERE nft_interactions / total_interactions >= {self.threshold}
        ORDER BY nft_ratio DESC
        LIMIT 1000
        """
        return self.bq_client.execute_query(query)

    def generate_labels(self) -> List[AddressLabel]:
        """Generate NFT trader labels for addresses with high NFT activity.

        Returns:
            List[AddressLabel]: List of NFT trader address labels
        """
        df = self._get_nft_traders()

        labels = []
        for _, row in df.iterrows():
            # Calculate confidence based on NFT ratio and activity level
            nft_ratio = row['nft_ratio']
            total_interactions = row['total_interactions']

            # Base confidence from NFT ratio
            ratio_confidence = nft_ratio

            # Activity bonus (more interactions = higher confidence)
            activity_bonus = min(
                0.2, total_interactions / 100.0)  # Max 20% bonus

            # Final confidence with activity bonus
            confidence = min(1.0, ratio_confidence + activity_bonus)

            # Ensure minimum confidence
            confidence = max(0.4, confidence)

            label = AddressLabel(
                address=row['address'],
                label=self.label_type,
                confidence=confidence,
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                source_rule=f'nft_ratio >= {self.threshold}'
            )
            labels.append(label)

        return labels

    def get_threshold(self) -> float:
        """Get the current NFT ratio threshold."""
        return self.threshold

    def set_threshold(self, threshold: float):
        """Set a new NFT ratio threshold.

        Args:
            threshold: New NFT interaction ratio threshold (0.0-1.0)
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")

        self.threshold = threshold
        logger.info(f"Updated NFT trader threshold to {threshold}")

    def get_min_activity(self) -> int:
        """Get the minimum activity threshold."""
        return self.min_activity

    def set_min_activity(self, min_activity: int):
        """Set the minimum activity threshold.

        Args:
            min_activity: New minimum total interactions required
        """
        self.min_activity = min_activity
        logger.info(f"Updated NFT trader minimum activity to {min_activity}")

    def get_confidence_calculation_info(self) -> dict:
        """Get information about how confidence is calculated.

        Returns:
            dict: Confidence calculation parameters
        """
        return {
            'threshold': self.threshold,
            'min_activity': self.min_activity,
            'ratio_confidence': 'nft_ratio',
            'activity_bonus_formula': 'min(0.2, total_interactions / 100.0)',
            'final_formula': 'min(1.0, ratio_confidence + activity_bonus)',
            'min_confidence': 0.4,
            'description': 'Confidence based on NFT ratio with activity bonus'
        }
