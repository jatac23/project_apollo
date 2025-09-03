# Apollo Project Structure

```
project_apollo/
├── README.md                    # Main documentation
├── requirements.txt             # Python dependencies
├── config.py                   # Configuration settings
├── main.py                     # Main execution script
├── setup.py                    # Setup and installation script
├── test_pipeline.py            # Unit tests
├── example_usage.py            # Usage examples
├── .gitignore                  # Git ignore rules
├── PROJECT_STRUCTURE.md        # This file
└── src/                        # Source code directory
    ├── __init__.py
    ├── models.py               # Data models (Pydantic)
    ├── bigquery_client.py      # BigQuery client wrapper
    └── labeling_pipeline.py    # Core labeling logic
```

## Key Components

### Core Pipeline (`src/labeling_pipeline.py`)
- **LabelingPipeline**: Main pipeline class
- **generate_whale_labels()**: Identifies high ETH balance addresses
- **generate_nft_trader_labels()**: Finds NFT-focused traders
- **generate_dex_user_labels()**: Identifies DEX users
- **generate_new_wallet_labels()**: Finds recently created wallets

### BigQuery Integration (`src/bigquery_client.py`)
- **BigQueryClient**: Wrapper for Google BigQuery operations
- **get_ethereum_balances()**: Query ETH balances
- **get_nft_traders()**: Query NFT interaction patterns
- **get_dex_users()**: Query DEX contract interactions
- **get_new_wallets()**: Query recent first transactions

### Data Models (`src/models.py`)
- **AddressLabel**: Standardized label format
- **LabelCandidate**: Processing candidate format

### Configuration (`config.py`)
- Environment-based configuration
- Configurable thresholds and parameters
- Google Cloud settings

## Usage

1. **Setup**: `python setup.py`
2. **Run Pipeline**: `python main.py`
3. **Run Tests**: `python test_pipeline.py`
4. **Examples**: `python example_usage.py`

## Output

- CSV files in `output/` directory
- Standardized schema with confidence scores
- Timestamped results for tracking
