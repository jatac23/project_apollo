# Apollo Docker Setup Guide

This guide will help you run the Apollo blockchain address labeling pipeline using Docker, making it easy to share and deploy across different environments.

## 🐳 Quick Start with Docker

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Google Cloud Project** with BigQuery API enabled
- **Service Account** with BigQuery permissions

### 1. Clone and Setup

```bash
git clone <repository-url>
cd project_apollo
```

### 2. Configure Credentials

1. **Create credentials directory:**
   ```bash
   mkdir credentials
   ```

2. **Place your Google Cloud service account key:**
   - Download your service account JSON key from Google Cloud Console
   - Place it in the `credentials/` directory
   - Rename it to `service-account-key.json`

3. **Configure environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your Google Cloud project ID
   ```

### 3. Run the Pipeline

**Option A: Using the helper script (Recommended)**
```bash
./docker-run.sh run
```

**Option B: Using Docker Compose directly**
```bash
docker-compose build
docker-compose run --rm apollo
```

## 🛠️ Available Commands

The `docker-run.sh` script provides several convenient commands:

```bash
# Build the Docker image
./docker-run.sh build

# Run the labeling pipeline
./docker-run.sh run

# Run in development mode (with live code mounting)
./docker-run.sh dev

# Run setup validation
./docker-run.sh validate

# Show container logs
./docker-run.sh logs

# Clean up Docker resources
./docker-run.sh cleanup

# Show help
./docker-run.sh help
```

## 🔧 Development Mode

For development with live code reloading:

```bash
./docker-run.sh dev
```

This mounts your source code into the container, so changes are reflected immediately without rebuilding.

## 📁 Directory Structure

```
project_apollo/
├── credentials/
│   └── service-account-key.json    # Your Google Cloud credentials
├── output/                         # Generated CSV files
├── .env                           # Environment configuration
├── docker-compose.yml             # Docker Compose configuration
├── Dockerfile                     # Docker image definition
├── docker-run.sh                  # Helper script
└── ...                           # Source code
```

## 🔒 Security Best Practices

### Credentials Management

1. **Never commit credentials to version control:**
   ```bash
   # Add to .gitignore
   credentials/
   .env
   ```

2. **Use environment variables in production:**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   ```

3. **Consider using Docker secrets for production:**
   ```yaml
   # docker-compose.prod.yml
   services:
     apollo:
       secrets:
         - google_credentials
   secrets:
     google_credentials:
       file: ./credentials/service-account-key.json
   ```

## 🚀 Production Deployment

### Using Docker Compose

```bash
# Production deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Using Docker directly

```bash
# Build image
docker build -t apollo-labeling-pipeline .

# Run with environment variables
docker run --rm \
  -v $(pwd)/credentials:/app/credentials:ro \
  -v $(pwd)/output:/app/output \
  -e GOOGLE_CLOUD_PROJECT=your-project-id \
  apollo-labeling-pipeline
```

## 🔍 Troubleshooting

### Common Issues

1. **"Credentials file not found"**
   ```bash
   # Check if credentials directory exists
   ls -la credentials/
   
   # Ensure the file is named correctly
   ls -la credentials/service-account-key.json
   ```

2. **"Permission denied"**
   ```bash
   # Make sure the script is executable
   chmod +x docker-run.sh
   ```

3. **"Docker not found"**
   - Install Docker and Docker Compose
   - Ensure Docker daemon is running

4. **"BigQuery API not enabled"**
   - Enable BigQuery API in your Google Cloud Console
   - Verify your service account has the required permissions

### Debug Mode

Run with verbose output:
```bash
docker-compose run --rm apollo python -c "
import os
print('Environment variables:')
for key, value in os.environ.items():
    if 'GOOGLE' in key or 'BIGQUERY' in key:
        print(f'{key}={value}')
"
```

## 📊 Output

The pipeline generates CSV files in the `output/` directory:

```bash
# View generated files
ls -la output/

# View the latest results
tail -f output/apollo_labels_*.csv
```

## 🔄 Updating the Pipeline

To update the pipeline with new code:

```bash
# Pull latest changes
git pull

# Rebuild and run
./docker-run.sh build
./docker-run.sh run
```

## 📝 Environment Variables

All configuration can be done through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_CLOUD_PROJECT` | Your Google Cloud project ID | Required |
| `BIGQUERY_DATASET` | BigQuery dataset name | `apollo_labels` |
| `BIGQUERY_LOCATION` | BigQuery location | `US` |
| `MIN_ETH_BALANCE_WHALE` | Minimum ETH for whale label | `1000.0` |
| `NFT_TRADER_THRESHOLD` | NFT trader threshold | `0.7` |
| `LOOKBACK_DAYS_NEW_WALLET` | New wallet lookback days | `30` |

## 🤝 Contributing

When contributing to the Docker setup:

1. Test your changes with `./docker-run.sh validate`
2. Ensure the image builds successfully
3. Update documentation if needed
4. Test both development and production modes

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run `./docker-run.sh validate` to check your setup
3. Check the logs with `./docker-run.sh logs`
4. Ensure your Google Cloud credentials are properly configured
