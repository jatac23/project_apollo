"""Core labeling pipeline for Apollo blockchain address labeling."""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import logging

from .bigquery_client import BigQueryClient
from .models import AddressLabel, LabelCandidate
from config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LabelingPipeline:
    """Main pipeline for generating blockchain address labels."""

    def __init__(self):
        """Initialize the labeling pipeline."""
        self.bq_client = BigQueryClient()
        self.labels: List[AddressLabel] = []

    def generate_whale_labels(self) -> List[AddressLabel]:
        """Generate whale labels for addresses with high ETH balance."""
        logger.info("Generating whale labels...")

        try:
            df = self.bq_client.get_ethereum_balances(
                settings.min_eth_balance_whale)

            labels = []
            for _, row in df.iterrows():
                # Calculate confidence based on balance (higher balance = higher confidence)
                confidence = min(
                    1.0, row['eth_balance'] / (settings.min_eth_balance_whale * 10))

                label = AddressLabel(
                    address=row['address'],
                    label='whale',
                    confidence=confidence,
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    source_rule=f'eth_balance >= {settings.min_eth_balance_whale}'
                )
                labels.append(label)

            logger.info(f"Generated {len(labels)} whale labels")
            return labels

        except Exception as e:
            logger.error(f"Error generating whale labels: {e}")
            return []

    def generate_nft_trader_labels(self) -> List[AddressLabel]:
        """Generate NFT trader labels for addresses with high ERC-721 interaction ratio."""
        logger.info("Generating NFT trader labels...")

        try:
            df = self.bq_client.get_nft_traders(settings.nft_trader_threshold)

            labels = []
            for _, row in df.iterrows():
                # Confidence based on NFT ratio and total interactions
                base_confidence = row['nft_ratio']
                # Up to 20% boost for high activity
                activity_boost = min(0.2, row['total_interactions'] / 1000)
                confidence = min(1.0, base_confidence + activity_boost)

                label = AddressLabel(
                    address=row['address'],
                    label='nft_trader',
                    confidence=confidence,
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    source_rule=f'nft_interaction_ratio >= {settings.nft_trader_threshold}'
                )
                labels.append(label)

            logger.info(f"Generated {len(labels)} NFT trader labels")
            return labels

        except Exception as e:
            logger.error(f"Error generating NFT trader labels: {e}")
            return []

    def generate_dex_user_labels(self) -> List[AddressLabel]:
        """Generate DEX user labels for addresses that interact with DEX contracts."""
        logger.info("Generating DEX user labels...")

        try:
            df = self.bq_client.get_dex_users()

            labels = []
            for _, row in df.iterrows():
                # Confidence based on number of unique DEX contracts and total interactions
                unique_contracts_confidence = min(
                    0.6, row['unique_dex_contracts'] / 5)  # Up to 60% for 5+ contracts
                # Up to 40% for 100+ interactions
                activity_confidence = min(
                    0.4, row['total_dex_interactions'] / 100)
                confidence = min(
                    1.0, unique_contracts_confidence + activity_confidence)

                label = AddressLabel(
                    address=row['address'],
                    label='dex_user',
                    confidence=confidence,
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    source_rule='interacted_with_known_dex_contracts'
                )
                labels.append(label)

            logger.info(f"Generated {len(labels)} DEX user labels")
            return labels

        except Exception as e:
            logger.error(f"Error generating DEX user labels: {e}")
            return []

    def generate_new_wallet_labels(self) -> List[AddressLabel]:
        """Generate new wallet labels for addresses with recent first transactions."""
        logger.info("Generating new wallet labels...")

        try:
            df = self.bq_client.get_new_wallets(
                settings.lookback_days_new_wallet)

            labels = []
            for _, row in df.iterrows():
                # Confidence decreases as wallet gets older
                days_old = (datetime.now() -
                            row['first_transaction_time']).days
                confidence = max(
                    0.1, 1.0 - (days_old / settings.lookback_days_new_wallet))

                label = AddressLabel(
                    address=row['address'],
                    label='new_wallet',
                    confidence=confidence,
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    source_rule=f'first_transaction_within_{settings.lookback_days_new_wallet}_days'
                )
                labels.append(label)

            logger.info(f"Generated {len(labels)} new wallet labels")
            return labels

        except Exception as e:
            logger.error(f"Error generating new wallet labels: {e}")
            return []

    def run_full_pipeline(self) -> List[AddressLabel]:
        """Run the complete labeling pipeline."""
        logger.info("Starting full labeling pipeline...")

        all_labels = []

        # Generate all label types
        all_labels.extend(self.generate_whale_labels())
        all_labels.extend(self.generate_nft_trader_labels())
        all_labels.extend(self.generate_dex_user_labels())
        all_labels.extend(self.generate_new_wallet_labels())

        # Store labels for later processing
        self.labels = all_labels

        logger.info(
            f"Pipeline completed. Generated {len(all_labels)} total labels")
        return all_labels

    def get_labels_by_type(self, label_type: str) -> List[AddressLabel]:
        """Get all labels of a specific type."""
        return [label for label in self.labels if label.label == label_type]

    def get_labels_by_address(self, address: str) -> List[AddressLabel]:
        """Get all labels for a specific address."""
        return [label for label in self.labels if label.address.lower() == address.lower()]

    def export_to_dataframe(self) -> pd.DataFrame:
        """Export all labels to a pandas DataFrame."""
        if not self.labels:
            return pd.DataFrame()

        data = []
        for label in self.labels:
            data.append({
                'address': label.address,
                'label': label.label,
                'confidence': label.confidence,
                'created_at': label.created_at,
                'updated_at': label.updated_at,
                'source_rule': label.source_rule
            })

        return pd.DataFrame(data)
