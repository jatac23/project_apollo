"""BigQuery client for Apollo labeling pipeline."""

import os
from typing import List, Dict, Any, Optional
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import pandas as pd
from datetime import datetime, timedelta

from config import settings


class BigQueryClient:
    """BigQuery client wrapper for Apollo pipeline."""

    def __init__(self):
        """Initialize BigQuery client."""
        self.client = bigquery.Client(
            project=settings.google_cloud_project,
            location=settings.bigquery_location
        )
        self.dataset_id = f"{settings.google_cloud_project}.{settings.bigquery_dataset}"
        self._ensure_dataset_exists()

    def _ensure_dataset_exists(self):
        """Ensure the dataset exists."""
        try:
            self.client.get_dataset(self.dataset_id)
        except NotFound:
            dataset = bigquery.Dataset(self.dataset_id)
            dataset.location = settings.bigquery_location
            self.client.create_dataset(dataset, timeout=30)
            print(f"Created dataset {self.dataset_id}")

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a BigQuery SQL query and return results as DataFrame."""
        try:
            query_job = self.client.query(query)
            return query_job.to_dataframe()
        except Exception as e:
            print(f"Error executing query: {e}")
            raise

    def get_ethereum_balances(self, min_balance: float = 1000.0) -> pd.DataFrame:
        """Get Ethereum addresses with balances above threshold."""
        query = f"""
        SELECT 
            address,
            eth_balance,
            CURRENT_TIMESTAMP() as created_at,
            CURRENT_TIMESTAMP() as updated_at
        FROM (
            SELECT 
                address,
                SUM(value) / 1e18 as eth_balance
            FROM `bigquery-public-data.crypto_ethereum.balances`
            WHERE block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
            GROUP BY address
            HAVING eth_balance >= {min_balance}
        )
        ORDER BY eth_balance DESC
        """
        return self.execute_query(query)

    def get_nft_traders(self, threshold: float = 0.7) -> pd.DataFrame:
        """Get addresses with high percentage of ERC-721 interactions."""
        query = f"""
        WITH address_interactions AS (
            SELECT 
                from_address as address,
                COUNT(*) as total_interactions,
                SUM(CASE WHEN token_standard = 'ERC-721' THEN 1 ELSE 0 END) as nft_interactions
            FROM `bigquery-public-data.crypto_ethereum.token_transfers`
            WHERE block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
            GROUP BY from_address
            HAVING total_interactions >= 10  -- Minimum activity threshold
        )
        SELECT 
            address,
            nft_interactions / total_interactions as nft_ratio,
            total_interactions,
            nft_interactions,
            CURRENT_TIMESTAMP() as created_at,
            CURRENT_TIMESTAMP() as updated_at
        FROM address_interactions
        WHERE nft_interactions / total_interactions >= {threshold}
        ORDER BY nft_ratio DESC
        """
        return self.execute_query(query)

    def get_dex_users(self) -> pd.DataFrame:
        """Get addresses that have interacted with known DEX router contracts."""
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
        WHERE block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
        AND to_address IN ('{contracts_str}')
        GROUP BY from_address
        HAVING total_dex_interactions >= 5  -- Minimum DEX activity
        ORDER BY total_dex_interactions DESC
        """
        return self.execute_query(query)

    def get_new_wallets(self, days: int = 30) -> pd.DataFrame:
        """Get addresses with first transaction within specified days."""
        query = f"""
        WITH first_transactions AS (
            SELECT 
                from_address as address,
                MIN(block_timestamp) as first_transaction_time
            FROM `bigquery-public-data.crypto_ethereum.transactions`
            GROUP BY from_address
        )
        SELECT 
            address,
            first_transaction_time,
            CURRENT_TIMESTAMP() as created_at,
            CURRENT_TIMESTAMP() as updated_at
        FROM first_transactions
        WHERE first_transaction_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        ORDER BY first_transaction_time DESC
        """
        return self.execute_query(query)
