"""Example usage of the Apollo labeling pipeline."""

from src.labeling_pipeline import LabelingPipeline
import os
import sys
import pandas as pd

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def example_whale_analysis():
    """Example: Analyze whale addresses."""
    print("=== WHALE ANALYSIS EXAMPLE ===")

    pipeline = LabelingPipeline()
    whale_labels = pipeline.generate_whale_labels()

    if whale_labels:
        print(f"Found {len(whale_labels)} whale addresses")

        # Show top 5 whales by confidence
        whale_df = pd.DataFrame([{
            'address': label.address,
            'confidence': label.confidence,
            'source_rule': label.source_rule
        } for label in whale_labels])

        top_whales = whale_df.nlargest(5, 'confidence')
        print("\nTop 5 whales by confidence:")
        for _, whale in top_whales.iterrows():
            print(
                f"  {whale['address'][:10]}... | Confidence: {whale['confidence']:.3f}")
    else:
        print("No whale addresses found")


def example_multi_label_addresses():
    """Example: Find addresses with multiple labels."""
    print("\n=== MULTI-LABEL ADDRESSES EXAMPLE ===")

    pipeline = LabelingPipeline()
    all_labels = pipeline.run_full_pipeline()

    if all_labels:
        # Group by address to find multi-label addresses
        address_labels = {}
        for label in all_labels:
            if label.address not in address_labels:
                address_labels[label.address] = []
            address_labels[label.address].append(label.label)

        multi_label_addresses = {
            addr: labels for addr, labels in address_labels.items()
            if len(set(labels)) > 1
        }

        print(
            f"Found {len(multi_label_addresses)} addresses with multiple labels")

        # Show examples
        for i, (address, labels) in enumerate(list(multi_label_addresses.items())[:5]):
            unique_labels = list(set(labels))
            print(f"  {address[:10]}... | Labels: {', '.join(unique_labels)}")

            if i >= 4:  # Show only first 5
                break
    else:
        print("No labels generated")


def example_confidence_analysis():
    """Example: Analyze label confidence distribution."""
    print("\n=== CONFIDENCE ANALYSIS EXAMPLE ===")

    pipeline = LabelingPipeline()
    all_labels = pipeline.run_full_pipeline()

    if all_labels:
        df = pipeline.export_to_dataframe()

        print(f"Total labels: {len(df)}")
        print(f"Mean confidence: {df['confidence'].mean():.3f}")
        print(f"Median confidence: {df['confidence'].median():.3f}")

        # Confidence by label type
        print("\nConfidence by label type:")
        for label_type in df['label'].unique():
            subset = df[df['label'] == label_type]
            print(
                f"  {label_type}: {subset['confidence'].mean():.3f} (n={len(subset)})")

        # High confidence labels
        high_conf = df[df['confidence'] >= 0.8]
        print(
            f"\nHigh confidence labels (>=0.8): {len(high_conf)} ({len(high_conf)/len(df)*100:.1f}%)")
    else:
        print("No labels generated")


if __name__ == "__main__":
    print("Apollo Labeling Pipeline - Example Usage")
    print("=" * 50)

    try:
        example_whale_analysis()
        example_multi_label_addresses()
        example_confidence_analysis()

        print("\n" + "=" * 50)
        print("Examples completed successfully!")

    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have configured your Google Cloud credentials.")
