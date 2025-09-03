from typing import List
import logging
import pandas as pd

from .base_labeler import BaseLabeler
from ..models import AddressLabel
from config import settings

logger = logging.getLogger(__name__)


class WhaleLabeler(BaseLabeler):
    def __init__(self, bq_client=None, min_balance: float = None):
        super().__init__(bq_client)
        self.min_balance = min_balance or settings.min_eth_balance_whale
        self.label_type = 'whale'

    def _get_ethereum_balances(self) -> pd.DataFrame:
        query = f"""
        SELECT 
            address,
            eth_balance,
            CURRENT_TIMESTAMP() as created_at,
            CURRENT_TIMESTAMP() as updated_at
        FROM (
            SELECT 
                address,
                SUM(eth_balance) as eth_balance
            FROM `bigquery-public-data.crypto_ethereum.balances`
            GROUP BY address
            HAVING eth_balance >= {self.min_balance}
        )
        ORDER BY eth_balance DESC
        LIMIT 1000
        """
        return self.bq_client.execute_query(query)

    def generate_labels(self) -> List[AddressLabel]:
        df = self._get_ethereum_balances()

        labels = []
        for _, row in df.iterrows():
            eth_balance = float(row['eth_balance'])
            confidence = min(
                1.0, eth_balance / (self.min_balance * 10))

            label = AddressLabel(
                address=row['address'],
                label=self.label_type,
                confidence=confidence,
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                source_rule=f'eth_balance >= {self.min_balance}'
            )
            labels.append(label)

        return labels

    def get_balance_threshold(self) -> float:
        return self.min_balance

    def set_balance_threshold(self, threshold: float):
        self.min_balance = threshold
        logger.info(f"Updated whale balance threshold to {threshold} ETH")

    def get_confidence_calculation_info(self) -> dict:
        return {
            'min_balance': self.min_balance,
            'max_confidence_threshold': self.min_balance * 10,
            'formula': 'min(1.0, eth_balance / (min_balance * 10))',
            'description': 'Confidence scales with balance, capped at 1.0'
        }
