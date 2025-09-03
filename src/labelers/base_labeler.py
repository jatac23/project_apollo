"""Base labeler class for Apollo blockchain address labeling pipeline."""

from abc import ABC, abstractmethod
from typing import List
import logging

from ..models import AddressLabel
from ..bigquery_client import BigQueryClient
from config import settings

logger = logging.getLogger(__name__)


class BaseLabeler(ABC):
    """Base class for all address labelers."""

    def __init__(self, bq_client: BigQueryClient = None):
        """Initialize the labeler with BigQuery client."""
        self.bq_client = bq_client or BigQueryClient()
        self.label_type = self.__class__.__name__.replace(
            'Labeler', '').lower()

    @abstractmethod
    def generate_labels(self) -> List[AddressLabel]:
        """Generate labels for addresses based on specific criteria.

        Returns:
            List[AddressLabel]: List of generated address labels
        """
        pass

    def get_label_type(self) -> str:
        """Get the label type for this labeler."""
        return self.label_type

    def log_generation_start(self):
        """Log the start of label generation."""
        logger.info(f"Generating {self.label_type} labels...")

    def log_generation_complete(self, labels: List[AddressLabel]):
        """Log the completion of label generation."""
        logger.info(f"Generated {len(labels)} {self.label_type} labels")

    def log_generation_error(self, error: Exception):
        """Log an error during label generation."""
        logger.error(f"Error generating {self.label_type} labels: {error}")

    def run(self) -> List[AddressLabel]:
        """Run the labeler and return generated labels.

        Returns:
            List[AddressLabel]: List of generated labels, empty list on error
        """
        try:
            self.log_generation_start()
            labels = self.generate_labels()
            self.log_generation_complete(labels)
            return labels
        except Exception as e:
            self.log_generation_error(e)
            return []
