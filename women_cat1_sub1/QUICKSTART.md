# Quick Start Guide

## 5-Minute Setup

### 1. **Clone Repository**
```bash
git clone https://github.com/yourusername/Project8-Baat.git
cd Project8-Baat
```

### 2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Set AWS Credentials**

**Option A: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_S3_BUCKET=your-bucket-name
```

**Option B: .env File**
```bash
# Create .env file in project root
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET=your-bucket-name
```

Then update config.py to load from .env:
```python
from dotenv import load_dotenv
import os
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
```

### 5. **Test Connection**
```bash
python -c "from src.s3_uploader import S3Uploader; S3Uploader().test_connection()"
```

### 6. **Run Scraper**
```bash
python -m src.main
```

## GitHub Actions Setup (1-Minute)

### 1. **Go to Repository Settings**
- Click Settings → Secrets and variables → Actions

### 2. **Add Three Secrets**
```
AWS_ACCESS_KEY_ID = (your key)
AWS_SECRET_ACCESS_KEY = (your secret)
AWS_S3_BUCKET = (your bucket)
```

### 3. **Done!**
- Workflow runs automatically daily at 2 AM UTC
- Or manually trigger from Actions tab

## Verify Installation

```bash
# Check Python version
python --version

# Check dependencies
pip list | grep -E "requests|beautifulsoup4|boto3|openpyxl"

# Test imports
python -c "from src.scraper import BoutiqaatScraper; print('✓ Scraper OK')"
python -c "from src.s3_uploader import S3Uploader; print('✓ S3 Uploader OK')"
python -c "from src.excel_generator import ExcelGenerator; print('✓ Excel Generator OK')"
```

## First Run

Your first run will:
1. ✅ Scrape all makeup categories
2. ✅ Scrape all subcategories
3. ✅ Scrape all products with details
4. ✅ Download and upload images to S3
5. ✅ Generate Excel reports
6. ✅ Upload Excel files to S3

**Expected Output:**
```
INFO - Starting Boutiqaat Data Pipeline
INFO - S3 connection successful
INFO - Found 8 categories
INFO - Processing Category: Women Makeup
...
INFO - Pipeline completed successfully
```

## Output Locations

### Excel Files
```
s3://your-bucket/boutiqaat-data/year=2026/month=03/day=03/women-makeup/
├── Face_2026-03-03.xlsx
├── Eyes_2026-03-03.xlsx
└── ...
```

### Product Images
```
s3://your-bucket/boutiqaat-data/year=2026/month=03/day=03/women-makeup/images/
├── SKU1_image.jpg
├── SKU2_image.jpg
└── ...
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'src'"
```bash
pip install -r requirements.txt
# Make sure you're in the project root directory
```

### "ClientError: The specified bucket does not exist"
- Check bucket name in secrets (exact match)
- Verify bucket exists in AWS S3
- Check AWS credentials have S3 access

### "AccessDenied" errors
- Verify IAM user has S3 permissions
- Check AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
- Review attached policies

### "ConnectTimeout" errors
- Check internet connection
- Verify website is accessible
- Increase REQUEST_TIMEOUT in config.py

## Next Steps

1. **Monitor First Run**: Check GitHub Actions logs
2. **Verify S3 Upload**: Check S3 bucket for files
3. **Review Excel Output**: Download Excel files and validate
4. **Customize Settings**: Edit config.py as needed
5. **Schedule Adjustments**: Modify cron in .github/workflows/scrape-daily.yml

## Advanced Options

### Change Daily Schedule
Edit `.github/workflows/scrape-daily.yml`:
```yaml
schedule:
  - cron: '0 2 * * *'  # Change times here (UTC)
```

Common times:
- `0 2 * * *` = 2:00 AM UTC
- `0 10 * * *` = 10:00 AM UTC
- `0 18 * * *` = 6:00 PM UTC
- `0 0 * * 0` = Every Sunday at midnight UTC

### Adjust Image Quality
Edit `config.py`:
```python
IMAGE_QUALITY = 80  # 0-100, higher = better quality
MAX_IMAGE_SIZE = (400, 400)  # Resize dimensions
```

### Increase Scraping Timeout
Edit `config.py`:
```python
REQUEST_TIMEOUT = 30  # Seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # Seconds
```

## Getting Help

📖 **Full Documentation**: See [README.md](README.md)
🐛 **Report Issues**: Create GitHub Issue
💬 **Questions**: Check GitHub Discussions

---

**Happy Scraping! 🚀**
