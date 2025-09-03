"""Configuration settings for the Apollo labeling pipeline."""

import os
from typing import Optional


class Settings:
    """Application settings."""

    def __init__(self):
        # Google Cloud Configuration
        self.google_application_credentials: Optional[str] = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS")
        self.google_cloud_project: Optional[str] = os.getenv(
            "GOOGLE_CLOUD_PROJECT")

        # BigQuery Configuration
        self.bigquery_dataset: str = os.getenv(
            "BIGQUERY_DATASET", "apollo_labels")
        self.bigquery_location: str = os.getenv("BIGQUERY_LOCATION", "US")

        # Pipeline Configuration
        self.min_eth_balance_whale: float = float(
            os.getenv("MIN_ETH_BALANCE_WHALE", "1000.0"))
        self.nft_trader_threshold: float = float(
            os.getenv("NFT_TRADER_THRESHOLD", "0.7"))
        self.lookback_days_new_wallet: int = int(
            os.getenv("LOOKBACK_DAYS_NEW_WALLET", "30"))


# Global settings instance
settings = Settings()
