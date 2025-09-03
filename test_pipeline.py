"""Simple tests for the Apollo labeling pipeline."""

from src.models import AddressLabel
from src.labeling_pipeline import LabelingPipeline
import os
import sys
import unittest
from unittest.mock import Mock, patch
import pandas as pd
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


class TestLabelingPipeline(unittest.TestCase):
    """Test cases for the labeling pipeline."""

    def setUp(self):
        """Set up test fixtures."""
        self.pipeline = LabelingPipeline()

    def test_address_label_model(self):
        """Test AddressLabel model validation."""
        label = AddressLabel(
            address="0x1234567890123456789012345678901234567890",
            label="whale",
            confidence=0.95,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            source_rule="eth_balance >= 1000"
        )

        self.assertEqual(
            label.address, "0x1234567890123456789012345678901234567890")
        self.assertEqual(label.label, "whale")
        self.assertEqual(label.confidence, 0.95)
        self.assertEqual(label.source_rule, "eth_balance >= 1000")

    @patch('src.labeling_pipeline.BigQueryClient')
    def test_whale_label_generation(self, mock_bq_client):
        """Test whale label generation with mocked data."""
        # Mock BigQuery response
        mock_df = pd.DataFrame({
            'address': ['0x1234...', '0x5678...'],
            'eth_balance': [1500.0, 2500.0],
            'created_at': [datetime.now(), datetime.now()],
            'updated_at': [datetime.now(), datetime.now()]
        })

        mock_client_instance = Mock()
        mock_client_instance.get_ethereum_balances.return_value = mock_df
        mock_bq_client.return_value = mock_client_instance

        # Create new pipeline instance to use mocked client
        pipeline = LabelingPipeline()
        pipeline.bq_client = mock_client_instance

        labels = pipeline.generate_whale_labels()

        self.assertEqual(len(labels), 2)
        self.assertEqual(labels[0].label, "whale")
        self.assertEqual(labels[0].address, "0x1234...")
        self.assertGreater(labels[0].confidence, 0.0)
        self.assertLessEqual(labels[0].confidence, 1.0)

    @patch('src.labeling_pipeline.BigQueryClient')
    def test_nft_trader_label_generation(self, mock_bq_client):
        """Test NFT trader label generation with mocked data."""
        # Mock BigQuery response
        mock_df = pd.DataFrame({
            'address': ['0xabcd...', '0xefgh...'],
            'nft_ratio': [0.8, 0.9],
            'total_interactions': [100, 200],
            'nft_interactions': [80, 180],
            'created_at': [datetime.now(), datetime.now()],
            'updated_at': [datetime.now(), datetime.now()]
        })

        mock_client_instance = Mock()
        mock_client_instance.get_nft_traders.return_value = mock_df
        mock_bq_client.return_value = mock_client_instance

        pipeline = LabelingPipeline()
        pipeline.bq_client = mock_client_instance

        labels = pipeline.generate_nft_trader_labels()

        self.assertEqual(len(labels), 2)
        self.assertEqual(labels[0].label, "nft_trader")
        self.assertEqual(labels[0].address, "0xabcd...")
        self.assertGreater(labels[0].confidence, 0.0)
        self.assertLessEqual(labels[0].confidence, 1.0)

    def test_export_to_dataframe(self):
        """Test DataFrame export functionality."""
        # Create sample labels
        labels = [
            AddressLabel(
                address="0x1234...",
                label="whale",
                confidence=0.95,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                source_rule="eth_balance >= 1000"
            ),
            AddressLabel(
                address="0x5678...",
                label="nft_trader",
                confidence=0.85,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                source_rule="nft_ratio >= 0.7"
            )
        ]

        self.pipeline.labels = labels
        df = self.pipeline.export_to_dataframe()

        self.assertEqual(len(df), 2)
        self.assertIn('address', df.columns)
        self.assertIn('label', df.columns)
        self.assertIn('confidence', df.columns)
        self.assertIn('source_rule', df.columns)

        # Check data integrity
        self.assertEqual(df.iloc[0]['address'], "0x1234...")
        self.assertEqual(df.iloc[0]['label'], "whale")
        self.assertEqual(df.iloc[0]['confidence'], 0.95)

    def test_get_labels_by_type(self):
        """Test filtering labels by type."""
        labels = [
            AddressLabel(
                address="0x1234...",
                label="whale",
                confidence=0.95,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                source_rule="eth_balance >= 1000"
            ),
            AddressLabel(
                address="0x5678...",
                label="nft_trader",
                confidence=0.85,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                source_rule="nft_ratio >= 0.7"
            ),
            AddressLabel(
                address="0x9abc...",
                label="whale",
                confidence=0.90,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                source_rule="eth_balance >= 1000"
            )
        ]

        self.pipeline.labels = labels

        whale_labels = self.pipeline.get_labels_by_type("whale")
        self.assertEqual(len(whale_labels), 2)

        nft_labels = self.pipeline.get_labels_by_type("nft_trader")
        self.assertEqual(len(nft_labels), 1)

        dex_labels = self.pipeline.get_labels_by_type("dex_user")
        self.assertEqual(len(dex_labels), 0)


def run_tests():
    """Run all tests."""
    print("Running Apollo Pipeline Tests...")
    print("=" * 40)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLabelingPipeline)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 40)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} error(s) occurred")

    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()
