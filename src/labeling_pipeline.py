import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from .bigquery_client import BigQueryClient
from .models import AddressLabel, LabelCandidate
from .labelers import (
    WhaleLabeler,
    DEXUserLabeler,
    NFTTraderLabeler,
    NewWalletLabeler
)
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LabelingPipeline:
    def __init__(self, bq_client: BigQueryClient = None):
        self.bq_client = bq_client or BigQueryClient()
        self.labels: List[AddressLabel] = []

        self.whale_labeler = WhaleLabeler(self.bq_client)
        self.dex_user_labeler = DEXUserLabeler(self.bq_client)
        self.nft_trader_labeler = NFTTraderLabeler(self.bq_client)
        self.new_wallet_labeler = NewWalletLabeler(self.bq_client)

        self.labelers = {
            'whale': self.whale_labeler,
            'dex_user': self.dex_user_labeler,
            'nft_trader': self.nft_trader_labeler,
            'new_wallet': self.new_wallet_labeler
        }

    def generate_whale_labels(self) -> List[AddressLabel]:
        return self.whale_labeler.run()

    def generate_dex_user_labels(self) -> List[AddressLabel]:
        return self.dex_user_labeler.run()

    def generate_nft_trader_labels(self) -> List[AddressLabel]:
        return self.nft_trader_labeler.run()

    def generate_new_wallet_labels(self) -> List[AddressLabel]:
        return self.new_wallet_labeler.run()

    def run_full_pipeline(self, label_types: Optional[List[str]] = None) -> List[AddressLabel]:
        logger.info("Starting full labeling pipeline...")

        if label_types is None:
            label_types = list(self.labelers.keys())

        all_labels = []

        for label_type in label_types:
            if label_type not in self.labelers:
                logger.warning(f"Unknown label type: {label_type}")
                continue

            labeler = self.labelers[label_type]
            labels = labeler.run()
            all_labels.extend(labels)

        self.labels = all_labels
        logger.info(
            f"Pipeline completed. Generated {len(all_labels)} total labels")

        return all_labels

    def run_specific_labeler(self, label_type: str) -> List[AddressLabel]:
        if label_type not in self.labelers:
            raise ValueError(f"Unknown label type: {label_type}")

        labeler = self.labelers[label_type]
        return labeler.run()

    def add_custom_labeler(self, label_type: str, labeler):
        self.labelers[label_type] = labeler
        logger.info(f"Added custom labeler: {label_type}")

    def get_available_labelers(self) -> List[str]:
        return list(self.labelers.keys())

    def get_labeler_info(self, label_type: str) -> Dict[str, Any]:
        """Get information about a specific labeler.

        Args:
            label_type: Type of labeler to get info for

        Returns:
            Dict[str, Any]: Labeler information
        """
        if label_type not in self.labelers:
            raise ValueError(f"Unknown label type: {label_type}")

        labeler = self.labelers[label_type]

        info = {
            'label_type': labeler.get_label_type(),
            'class_name': labeler.__class__.__name__,
            'available_methods': [method for method in dir(labeler)
                                  if not method.startswith('_')]
        }

        # Add confidence calculation info if available
        if hasattr(labeler, 'get_confidence_calculation_info'):
            info['confidence_calculation'] = labeler.get_confidence_calculation_info()

        return info

    def export_to_dataframe(self) -> pd.DataFrame:
        """Export all labels to a pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing all labels
        """
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

    def get_labels_by_type(self, label_type: str) -> List[AddressLabel]:
        """Get all labels of a specific type.

        Args:
            label_type: Type of labels to retrieve

        Returns:
            List[AddressLabel]: Labels of the specified type
        """
        return [label for label in self.labels if label.label == label_type]

    def get_high_confidence_labels(self, threshold: float = 0.8) -> List[AddressLabel]:
        """Get labels with confidence above threshold.

        Args:
            threshold: Minimum confidence threshold

        Returns:
            List[AddressLabel]: High confidence labels
        """
        return [label for label in self.labels if label.confidence >= threshold]

    def get_multi_label_addresses(self) -> Dict[str, List[str]]:
        """Get addresses that have multiple labels.

        Returns:
            Dict[str, List[str]]: Address to list of label types mapping
        """
        address_labels: Dict[str, List[str]] = {}

        for label in self.labels:
            if label.address not in address_labels:
                address_labels[label.address] = []
            address_labels[label.address].append(label.label)

        # Filter to only addresses with multiple unique labels
        multi_label_addresses = {
            address: list(set(labels))
            for address, labels in address_labels.items()
            if len(set(labels)) > 1
        }

        return multi_label_addresses

    def clear_labels(self):
        """Clear all stored labels."""
        self.labels = []
        logger.info("Cleared all stored labels")

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get comprehensive pipeline statistics.

        Returns:
            Dict[str, Any]: Pipeline statistics
        """
        if not self.labels:
            return {'total_labels': 0, 'unique_addresses': 0}

        df = self.export_to_dataframe()

        stats = {
            'total_labels': len(self.labels),
            'unique_addresses': df['address'].nunique(),
            'label_type_breakdown': df['label'].value_counts().to_dict(),
            'confidence_stats': {
                'mean': df['confidence'].mean(),
                'median': df['confidence'].median(),
                'min': df['confidence'].min(),
                'max': df['confidence'].max(),
                'std': df['confidence'].std()
            },
            'high_confidence_labels': len(df[df['confidence'] >= 0.8]),
            'multi_label_addresses': len(self.get_multi_label_addresses()),
            'available_labelers': self.get_available_labelers()
        }

        return stats
