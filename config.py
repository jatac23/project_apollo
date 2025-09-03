import os
from typing import Optional
from dotenv import load_dotenv


class Settings:
    def __init__(self):
        load_dotenv()

        self.google_application_credentials: Optional[str] = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS")
        self.google_cloud_project: Optional[str] = os.getenv(
            "GOOGLE_CLOUD_PROJECT")

        self.bigquery_dataset: str = os.getenv(
            "BIGQUERY_DATASET", "apollo_labels")
        self.bigquery_location: str = os.getenv("BIGQUERY_LOCATION", "US")

        self.min_eth_balance_whale: float = float(
            os.getenv("MIN_ETH_BALANCE_WHALE", "1000.0"))
        self.nft_trader_threshold: float = float(
            os.getenv("NFT_TRADER_THRESHOLD", "0.7"))
        self.lookback_days_new_wallet: int = int(
            os.getenv("LOOKBACK_DAYS_NEW_WALLET", "30"))

        self._validate_settings()

    def _validate_settings(self):
        if not self.google_application_credentials:
            raise ValueError(
                "GOOGLE_APPLICATION_CREDENTIALS environment variable is required. "
                "Please set it to the path of your Google Cloud service account key file."
            )

        if not self.google_cloud_project:
            raise ValueError(
                "GOOGLE_CLOUD_PROJECT environment variable is required. "
                "Please set it to your Google Cloud project ID."
            )

        if not os.path.exists(self.google_application_credentials):
            raise FileNotFoundError(
                f"Google Cloud credentials file not found: {self.google_application_credentials}. "
                "Please check the path in GOOGLE_APPLICATION_CREDENTIALS environment variable."
            )


settings = Settings()
