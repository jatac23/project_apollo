# Apollo: Blockchain Address Labeling Pipeline

A scalable, modular pipeline for generating valuable labels for Ethereum addresses using Google BigQuery's public Ethereum dataset. Built for the Nansen Data Engineer take-home challenge.

## 🎯 Overview

Apollo generates actionable labels for blockchain addresses that help investors and analysts understand on-chain behavior patterns. The pipeline identifies:

- **Whales**: Addresses with high ETH balances (>1,000 ETH)
- **NFT Traders**: Addresses with 70%+ ERC-721 token interactions
- **DEX Users**: Addresses that actively trade on decentralized exchanges
- **New Wallets**: Addresses with first transactions within the last 30 days

## 🏗️ Architecture

The pipeline follows a modular, incremental design inspired by modern data engineering practices:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   BigQuery      │    │  Labeling        │    │   CSV Output    │
│   Ethereum      │───▶│  Pipeline        │───▶│   (MVP)         │
│   Dataset       │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Key Design Principles

- **Transparency**: Each label has clear, rule-based logic
- **Incremental**: Process only new blockchain data, append-only results
- **Extensibility**: Adding new labels requires no changes to existing pipelines
- **Scalability**: Built on BigQuery for handling massive datasets

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Cloud Project with BigQuery API enabled
- Service account with BigQuery access

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd project_apollo
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Google Cloud**
   ```bash
   # Set up authentication
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   ```

4. **Run the pipeline**
   ```bash
   python main.py
   ```

## 📊 Label Definitions

### Whale Label
- **Criteria**: ETH balance ≥ 1,000 ETH
- **Confidence**: Scales with balance (higher balance = higher confidence)
- **Use Case**: Identify large holders for market analysis

### NFT Trader Label
- **Criteria**: ≥70% of token interactions are with ERC-721 contracts
- **Confidence**: Based on NFT interaction ratio + activity level
- **Use Case**: Find dedicated NFT collectors and traders

### DEX User Label
- **Criteria**: Interactions with known DEX router contracts
- **Confidence**: Based on number of unique DEX contracts + total interactions
- **Use Case**: Identify active DeFi traders

### New Wallet Label
- **Criteria**: First transaction within last 30 days
- **Confidence**: Decreases as wallet ages
- **Use Case**: Track new entrants to the ecosystem

## 🔧 Configuration

Edit `config.py` to customize pipeline behavior:

```python
# Minimum ETH balance for whale label
min_eth_balance_whale: float = 1000.0

# NFT trader threshold (percentage of ERC-721 interactions)
nft_trader_threshold: float = 0.7

# Lookback period for new wallet detection
lookback_days_new_wallet: int = 30
```

## 📈 Output Format

The pipeline generates CSV files with standardized schema:

| Column | Type | Description |
|--------|------|-------------|
| `address` | STRING | Ethereum address |
| `label` | STRING | Label type (whale, nft_trader, dex_user, new_wallet) |
| `confidence` | FLOAT64 | Confidence score (0.0-1.0) |
| `created_at` | TIMESTAMP | Label creation time |
| `updated_at` | TIMESTAMP | Last update time |
| `source_rule` | STRING | Rule that generated the label |

## 🛠️ Technology Choices & Trade-offs

### BigQuery
- **Pros**: Handles petabyte-scale data, built-in partitioning, cost-effective for large queries
- **Cons**: Query costs can add up, requires Google Cloud setup
- **Alternative**: Could use Apache Spark for on-premise deployment

### Python + Pandas
- **Pros**: Rapid development, rich ecosystem, easy to extend
- **Cons**: Memory limitations for very large datasets
- **Alternative**: Could use Apache Beam for streaming processing

### CSV Output (MVP)
- **Pros**: Simple, universal format, easy to analyze
- **Cons**: Not optimized for large-scale data sharing
- **Future**: Will migrate to Parquet + S3 for production

## 🚧 Future Improvements

### Phase 1: Enhanced Labeling
- [ ] Add MEV bot detection
- [ ] Implement DeFi protocol user classification
- [ ] Add cross-chain address resolution

### Phase 2: Infrastructure
- [ ] Migrate to Apache Airflow for orchestration
- [ ] Implement incremental processing with delta tables
- [ ] Add monitoring and alerting

### Phase 3: Scale & Performance
- [ ] Export to Parquet format for better compression
- [ ] Implement real-time streaming pipeline
- [ ] Add machine learning-based label confidence

### Phase 4: User Experience
- [ ] Build REST API for label queries
- [ ] Create web dashboard for label exploration
- [ ] Add label explanation and provenance tracking

## 📊 Sample Results

```
=== APOLLO LABELING PIPELINE SUMMARY ===
Total labels generated: 1,247
Unique addresses: 892

Label type breakdown:
  whale: 156
  nft_trader: 423
  dex_user: 567
  new_wallet: 101

Confidence statistics:
  Mean confidence: 0.742
  Median confidence: 0.780
  Min confidence: 0.100
  Max confidence: 1.000

High confidence labels (>= 0.8): 834
```

## 🤝 Contributing

This is a take-home challenge submission. For production use, consider:

1. Adding comprehensive unit tests
2. Implementing proper error handling and retries
3. Adding data quality checks and validation
4. Creating Docker containers for deployment
5. Setting up CI/CD pipelines

## 📄 License

This project is created for the Nansen Data Engineer take-home challenge.

---

**Built with ❤️ for the crypto data community**
