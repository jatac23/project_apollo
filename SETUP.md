# Apollo Blockchain Address Labeling Pipeline - Setup Guide

This guide will help you set up the Apollo blockchain address labeling pipeline with your own Google Cloud credentials.

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Google Cloud Project** with BigQuery API enabled
3. **Service Account** with BigQuery permissions

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Google Cloud Setup

### 2.1 Create a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your **Project ID** (you'll need this later)

### 2.2 Enable BigQuery API
1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "BigQuery API" and enable it

### 2.3 Create a Service Account
1. Go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Give it a name (e.g., "apollo-labeling-service")
4. Grant the following roles:
   - **BigQuery Data Viewer** (to read public datasets)
   - **BigQuery Job User** (to run queries)
   - **BigQuery Data Editor** (to create datasets and tables)

### 2.4 Generate Service Account Key
1. Click on your newly created service account
2. Go to the "Keys" tab
3. Click "Add Key" > "Create new key"
4. Choose "JSON" format
5. Download the key file and save it securely

## Step 3: Configure Environment Variables

### Option A: Using .env file (Recommended)

1. Copy the template file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your values:
   ```bash
   # Google Cloud Configuration
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
   GOOGLE_CLOUD_PROJECT=your-project-id
   
   # BigQuery Configuration (optional - defaults provided)
   BIGQUERY_DATASET=apollo_labels
   BIGQUERY_LOCATION=US
   
   # Pipeline Configuration (optional - defaults provided)
   MIN_ETH_BALANCE_WHALE=1000.0
   NFT_TRADER_THRESHOLD=0.7
   LOOKBACK_DAYS_NEW_WALLET=30
   ```

### Option B: Using Environment Variables

Set the environment variables in your shell:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

## Step 4: Test the Setup

Run the pipeline to verify everything is working:

```bash
python main.py
```

You should see output similar to:
```
INFO:__main__:Starting Apollo blockchain address labeling pipeline...
INFO:src.labeling_pipeline:Starting full labeling pipeline...
...
INFO:__main__:Pipeline completed successfully. Results saved to: output/apollo_labels_YYYYMMDD_HHMMSS.csv
```

## Troubleshooting

### Common Issues

1. **"Default credentials were not found"**
   - Make sure `GOOGLE_APPLICATION_CREDENTIALS` points to your service account key file
   - Verify the file path is correct and the file exists

2. **"Project not found"**
   - Check that `GOOGLE_CLOUD_PROJECT` is set to your correct project ID
   - Ensure the project ID matches exactly (case-sensitive)

3. **"Permission denied"**
   - Verify your service account has the required BigQuery permissions
   - Make sure the BigQuery API is enabled in your project

4. **"Dataset not found"**
   - The pipeline will automatically create the dataset if it doesn't exist
   - Ensure your service account has "BigQuery Data Editor" role

### Getting Help

If you encounter issues:
1. Check the error messages carefully - they often contain helpful hints
2. Verify your Google Cloud setup using the [BigQuery console](https://console.cloud.google.com/bigquery)
3. Test your credentials with a simple query in the BigQuery console

## Security Notes

- **Never commit your `.env` file or service account key to version control**
- Keep your service account key file secure and don't share it
- Consider using Google Cloud's Application Default Credentials for production deployments
- Regularly rotate your service account keys

## Next Steps

Once setup is complete, you can:
- Run the full pipeline: `python main.py`
- Run specific labelers: See `example_usage.py`
- Customize labeling parameters in your `.env` file
- Add custom labelers: See `src/labelers/example_custom_labeler.py`
