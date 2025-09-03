from config import settings
from src.labeling_pipeline import LabelingPipeline
import os
import sys
import pandas as pd
from datetime import datetime
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def export_to_csv(labels_df: pd.DataFrame, output_dir: str = "output") -> str:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"apollo_labels_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)

    labels_df.to_csv(filepath, index=False)
    logger.info(f"Exported {len(labels_df)} labels to {filepath}")

    return filepath


def generate_summary_report(labels_df: pd.DataFrame) -> None:
    if labels_df.empty:
        logger.warning("No labels generated")
        return

    logger.info("=== APOLLO LABELING PIPELINE SUMMARY ===")
    logger.info(f"Total labels generated: {len(labels_df)}")
    logger.info(f"Unique addresses: {labels_df['address'].nunique()}")

    label_counts = labels_df['label'].value_counts()
    logger.info("\nLabel type breakdown:")
    for label_type, count in label_counts.items():
        logger.info(f"  {label_type}: {count}")

    logger.info(f"\nConfidence statistics:")
    logger.info(f"  Mean confidence: {labels_df['confidence'].mean():.3f}")
    logger.info(f"  Median confidence: {labels_df['confidence'].median():.3f}")
    logger.info(f"  Min confidence: {labels_df['confidence'].min():.3f}")
    logger.info(f"  Max confidence: {labels_df['confidence'].max():.3f}")

    high_confidence = labels_df[labels_df['confidence'] >= 0.8]
    logger.info(f"\nHigh confidence labels (>= 0.8): {len(high_confidence)}")

    address_label_counts = labels_df['address'].value_counts()
    multi_label_addresses = address_label_counts[address_label_counts > 1]
    if not multi_label_addresses.empty:
        logger.info(
            f"\nAddresses with multiple labels: {len(multi_label_addresses)}")
        logger.info("Top multi-label addresses:")
        for address, count in multi_label_addresses.head(5).items():
            labels = labels_df[labels_df['address']
                               == address]['label'].tolist()
            logger.info(f"  {address}: {labels}")


def main():
    logger.info("Starting Apollo blockchain address labeling pipeline...")

    try:
        pipeline = LabelingPipeline()
        labels = pipeline.run_full_pipeline()

        if not labels:
            logger.warning(
                "No labels were generated. Check your BigQuery configuration and data access.")
            return

        labels_df = pipeline.export_to_dataframe()
        generate_summary_report(labels_df)
        output_file = export_to_csv(labels_df)

        logger.info(
            f"Pipeline completed successfully. Results saved to: {output_file}")

        logger.info("\nSample results:")
        sample_df = labels_df.head(10)
        for _, row in sample_df.iterrows():
            logger.info(
                f"  {row['address'][:10]}... | {row['label']} | {row['confidence']:.3f}")

    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")
        raise


if __name__ == "__main__":
    main()
