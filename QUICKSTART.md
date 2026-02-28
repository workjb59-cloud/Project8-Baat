# Quick Start Guide

## 🤖 GitHub Actions Setup (Recommended)

For automated daily scraping:

### 1. Configure GitHub Secrets

Go to your repository: `Settings → Secrets and variables → Actions → New repository secret`

Add these 4 secrets:
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key  
- `AWS_REGION` - AWS region (e.g., `us-east-1`)
- `S3_BUCKET_NAME` - S3 bucket name (e.g., `boutiqaat-data`)

### 2. Customize Scraping

Edit `scraping_config.py` to configure:
- Categories to scrape
- Brands to scrape
- Celebrities to scrape

### 3. Run Workflow

**Manual trigger:**
1. Go to `Actions` tab
2. Click `Daily Boutiqaat Scraper`
3. Click `Run workflow`

**Automatic:** Runs daily at 2 AM UTC

📖 [Read the complete GitHub Actions setup guide](GITHUB_ACTIONS_SETUP.md)

---

## 💻 Local Development Setup (Optional)

For local testing only.

## Prerequisites

1. Python 3.8 or higher
2. AWS Account with S3 access
3. AWS credentials (Access Key ID and Secret Access Key)

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure AWS Credentials (Local Only)

Create a `.env` file in the project root:

```bash
# Create .env file
touch .env  # or: New-Item .env on Windows
```

Add your credentials to `.env`:

```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
S3_BUCKET_NAME=boutiqaat-data
```

⚠️ **Important:** `.env` is gitignored and should never be committed!

### 3. Configure What to Scrape

Edit `scraping_config.py` to customize:
- Which categories to scrape
- Which brands to scrape
- Which celebrities to scrape

Or use the defaults provided.

### 4. Run the Scraper

**Option 1: Simple Run (Recommended)**
```bash
python run.py
```

**Option 2: Direct Run**
```bash
python main.py
```

**Option 3: Test Configuration First**
```bash
python test_config.py
```

## What Happens During Scraping?

1. **Scraping Phase**: Extracts product data from Boutiqaat
2. **Image Download Phase**: Downloads and optimizes product images
3. **Excel Generation Phase**: Creates organized Excel files
4. **S3 Upload Phase**: Uploads everything to S3

## Output Structure

### S3 Bucket Structure

```
s3://boutiqaat-data/
└── year=2026/
    └── month=02/
        └── day=28/
            ├── categories/
            │   ├── excel_files/
            │   │   ├── Makeup.xlsx
            │   │   └── Perfumes.xlsx
            │   └── images/
            │       ├── foundations/
            │       └── lipsticks/
            ├── brands/
            │   ├── excel_files/
            │   │   └── all_brands.xlsx
            │   └── images/
            │       ├── mac/
            │       └── nars/
            └── celebrities/
                ├── excel_files/
                │   ├── Kylie_Jenner.xlsx
                │   └── Sana_Mahdi_Ansari.xlsx
                └── images/
                    ├── kylie_jenner/
                    └── sana_mahdi_ansari/
```

### Local Files Created

- `boutiqaat_scraper.log` - Detailed logs
- `pipeline_results_YYYYMMDD.json` - Results summary

## Monitoring Progress

The scraper provides real-time progress:
- Progress bars for scraping each type
- Image download progress
- Excel file upload progress
- Detailed logging to console and file

## Example Commands

### Run with default configuration
```bash
python run.py
```

### Test your configuration
```bash
python test_config.py
```

### Check your scraping config
```bash
python scraping_config.py
```

## Troubleshooting

### AWS Credentials Not Found
```
Error: Unable to locate credentials
```
**Solution**: Make sure `.env` file exists with valid AWS credentials

### Import Error
```
ModuleNotFoundError: No module named 'scrapling'
```
**Solution**: Run `pip install -r requirements.txt`

### S3 Bucket Permission Error
```
Error: Access Denied
```
**Solution**: Verify your AWS credentials have S3 write permissions

### Timeout Errors
```
Error: Request timed out
```
**Solution**: Increase `REQUEST_TIMEOUT` in `config.py`

## Performance Tips

1. **Start Small**: Test with a few items first
2. **Monitor Costs**: S3 storage and requests have costs
3. **Rate Limiting**: The scraper already includes delays
4. **Bandwidth**: Image downloads can be bandwidth-intensive

## Next Steps

After successful scraping:

1. Check S3 bucket for uploaded files
2. Download Excel files from S3
3. Review `pipeline_results_*.json` for statistics
4. Check logs for any warnings or errors

## Advanced Usage

### Scrape Only Categories
Edit `scraping_config.py`:
```python
SCRAPE_CATEGORIES = True
SCRAPE_BRANDS = False
SCRAPE_CELEBRITIES = False
```

### Skip Image Downloads
```python
DOWNLOAD_IMAGES = False
```

### Use Without S3 (Local Only)
See `README.md` for programmatic usage examples.

## Getting Help

1. Check `boutiqaat_scraper.log` for detailed errors
2. Review `pipeline_results_*.json` for statistics
3. Read the full `README.md` for detailed documentation

## Important Notes

- ⚠️ Respect Boutiqaat's terms of service
- ⚠️ Scraping can take a long time for many items
- ⚠️ Monitor AWS costs for S3 usage
- ⚠️ Images are optimized to save storage space

## License

For educational and personal use only.
