"""New wallet labeler for recently created addresses."""

from typing import List
import logging
import pandas as pd
from datetime import datetime

from .base_labeler import BaseLabeler
from ..models import AddressLabel
from config import settings

logger = logging.getLogger(__name__)


class NewWalletLabeler(BaseLabeler):
    """Labeler for identifying recently created wallet addresses."""

    def __init__(self, bq_client=None, lookback_days: int = None):
        """Initialize new wallet labeler.

        Args:
            bq_client: BigQuery client instance
            lookback_days: Number of days to look back for new wallets (defaults to config)
        """
        super().__init__(bq_client)
        self.lookback_days = lookback_days or settings.lookback_days_new_wallet
        self.label_type = 'new_wallet'

    def _get_new_wallets(self) -> pd.DataFrame:
        """Get addresses with first transaction within specified days.
        
        Returns:
            pd.DataFrame: DataFrame with new wallet information
        """
        query = f"""
        WITH recent_transactions AS (
            SELECT DISTINCT from_address as address
            FROM `bigquery-public-data.crypto_ethereum.transactions`
            WHERE DATE(block_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL {self.lookback_days} DAY)
            AND from_address IS NOT NULL
            AND from_address != '0x0000000000000000000000000000000000000000'
        ),
        first_transactions AS (
            SELECT 
                rt.address,
                MIN(DATE(t.block_timestamp)) as first_transaction_date
            FROM recent_transactions rt
            JOIN `bigquery-public-data.crypto_ethereum.transactions` t
            ON rt.address = t.from_address
            GROUP BY rt.address
            HAVING first_transaction_date >= DATE_SUB(CURRENT_DATE(), INTERVAL {self.lookback_days} DAY)
        )
        SELECT 
            address,
            first_transaction_date,
            CURRENT_TIMESTAMP() as created_at,
            CURRENT_TIMESTAMP() as updated_at
        FROM first_transactions
        ORDER BY first_transaction_date DESC
        LIMIT 5000
        """
        return self.bq_client.execute_query(query)

    def generate_labels(self) -> List[AddressLabel]:
        """Generate new wallet labels for recently created addresses.

        Returns:
            List[AddressLabel]: List of new wallet address labels
        """
        df = self._get_new_wallets()

        labels = []
        for _, row in df.iterrows():
            # Calculate confidence based on wallet age (newer = higher confidence)
            # Convert date to datetime for comparison
            first_transaction_date = pd.to_datetime(
                row['first_transaction_date'])
            days_old = (datetime.now() - first_transaction_date).days

            # Confidence decreases as wallet gets older
            confidence = max(
                0.1, 1.0 - (days_old / self.lookback_days))

            label = AddressLabel(
                address=row['address'],
                label=self.label_type,
                confidence=confidence,
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                source_rule=f'first_transaction_within_{self.lookback_days}_days'
            )
            labels.append(label)

        return labels

    def get_lookback_days(self) -> int:
        """Get the current lookback period in days."""
        return self.lookback_days

    def set_lookback_days(self, lookback_days: int):
        """Set a new lookback period for new wallet detection.

        Args:
            lookback_days: New lookback period in days
        """
        if lookback_days <= 0:
            raise ValueError("Lookback days must be positive")

        self.lookback_days = lookback_days
        logger.info(
            f"Updated new wallet lookback period to {lookback_days} days")

    def get_confidence_calculation_info(self) -> dict:
        """Get information about how confidence is calculated.

        Returns:
            dict: Confidence calculation parameters
        """
        return {
            'lookback_days': self.lookback_days,
            'formula': 'max(0.1, 1.0 - (days_old / lookback_days))',
            'min_confidence': 0.1,
            'max_confidence': 1.0,
            'description': 'Confidence decreases as wallet age increases'
        }

    def get_wallet_age_distribution(self, labels: List[AddressLabel]) -> dict:
        """Get distribution of wallet ages in the generated labels.

        Args:
            labels: List of new wallet labels

        Returns:
            dict: Age distribution statistics
        """
        if not labels:
            return {}

        # This would require additional data processing
        # For now, return basic info
        return {
            'total_new_wallets': len(labels),
            'lookback_period_days': self.lookback_days,
            'note': 'Detailed age distribution requires additional data processing'
        }
