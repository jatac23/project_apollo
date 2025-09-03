import os
from typing import List, Dict, Any, Optional
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import pandas as pd
from datetime import datetime, timedelta

from config import settings


class BigQueryClient:
    def __init__(self):
        self.client = bigquery.Client(
            project=settings.google_cloud_project,
            location=settings.bigquery_location
        )
        self.dataset_id = f"{settings.google_cloud_project}.{settings.bigquery_dataset}"
        self._ensure_dataset_exists()

    def _ensure_dataset_exists(self):
        try:
            self.client.get_dataset(self.dataset_id)
        except NotFound:
            dataset = bigquery.Dataset(self.dataset_id)
            dataset.location = settings.bigquery_location
            self.client.create_dataset(dataset, timeout=30)

    def execute_query(self, query: str) -> pd.DataFrame:
        try:
            query_job = self.client.query(query)
            return query_job.to_dataframe()
        except Exception as e:
            raise

    def execute_query_with_params(self, query: str, params: Dict[str, Any]) -> pd.DataFrame:
        """Execute a parameterized BigQuery SQL query.

        Args:
            query: SQL query string with parameter placeholders
            params: Dictionary of parameter values

        Returns:
            pd.DataFrame: Query results as DataFrame
        """
        try:
            job_config = bigquery.QueryJobConfig()
            job_config.query_parameters = [
                bigquery.ScalarQueryParameter(key, "STRING", str(value))
                for key, value in params.items()
            ]

            query_job = self.client.query(query, job_config=job_config)
            return query_job.to_dataframe()
        except Exception as e:

            raise

    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get schema information for a BigQuery table.

        Args:
            table_name: Name of the table (e.g., 'crypto_ethereum.balances')

        Returns:
            List[Dict[str, Any]]: Table schema information
        """
        try:
            table_ref = self.client.get_table(
                f"bigquery-public-data.{table_name}")
            schema = []
            for field in table_ref.schema:
                schema.append({
                    'name': field.name,
                    'type': field.field_type,
                    'mode': field.mode,
                    'description': field.description
                })
            return schema
        except Exception as e:

            return []

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get basic information about a BigQuery table.

        Args:
            table_name: Name of the table

        Returns:
            Dict[str, Any]: Table information
        """
        try:
            table_ref = self.client.get_table(
                f"bigquery-public-data.{table_name}")
            return {
                'table_id': table_ref.table_id,
                'num_rows': table_ref.num_rows,
                'num_bytes': table_ref.num_bytes,
                'created': table_ref.created,
                'modified': table_ref.modified,
                'description': table_ref.description
            }
        except Exception as e:

            return {}

    def estimate_query_cost(self, query: str) -> Dict[str, Any]:
        """Estimate the cost of a BigQuery query.

        Args:
            query: SQL query string

        Returns:
            Dict[str, Any]: Cost estimation information
        """
        try:
            # Create a dry run job to estimate cost
            job_config = bigquery.QueryJobConfig(
                dry_run=True, use_query_cache=False)
            query_job = self.client.query(query, job_config=job_config)

            return {
                'total_bytes_processed': query_job.total_bytes_processed,
                # Rough estimate
                'estimated_cost_usd': query_job.total_bytes_processed / (1024**4) * 5,
                'cache_hit': query_job.cache_hit,
                'dry_run': True
            }
        except Exception as e:

            return {}

    def get_available_tables(self, dataset: str = "crypto_ethereum") -> List[str]:
        """Get list of available tables in a dataset.

        Args:
            dataset: Dataset name to query

        Returns:
            List[str]: List of table names
        """
        try:
            dataset_ref = self.client.dataset(
                dataset, project="bigquery-public-data")
            tables = list(self.client.list_tables(dataset_ref))
            return [table.table_id for table in tables]
        except Exception as e:

            return []

    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate a BigQuery query without executing it.

        Args:
            query: SQL query string to validate

        Returns:
            Dict[str, Any]: Validation results
        """
        try:
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = self.client.query(query, job_config=job_config)

            return {
                'valid': True,
                'total_bytes_processed': query_job.total_bytes_processed,
                'cache_hit': query_job.cache_hit,
                'errors': []
            }
        except Exception as e:
            return {
                'valid': False,
                'total_bytes_processed': 0,
                'cache_hit': False,
                'errors': [str(e)]
            }

    def get_query_job_info(self, job_id: str) -> Dict[str, Any]:
        """Get information about a specific query job.

        Args:
            job_id: BigQuery job ID

        Returns:
            Dict[str, Any]: Job information
        """
        try:
            job = self.client.get_job(job_id)
            return {
                'job_id': job.job_id,
                'state': job.state,
                'created': job.created,
                'started': job.started,
                'ended': job.ended,
                'total_bytes_processed': job.total_bytes_processed,
                'total_bytes_billed': job.total_bytes_billed,
                'cache_hit': job.cache_hit,
                'errors': [str(error) for error in job.errors] if job.errors else []
            }
        except Exception as e:

            return {}
