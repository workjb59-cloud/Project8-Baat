# Boutiqaat Data Scraper Pipeline

Automated web scraping pipeline for Boutiqaat makeup products with S3 storage and Excel report generation.

## Features

✅ **Automated Web Scraping**
- Scrapes categories, subcategories, and products from boutiqaat.com
- Extracts detailed product information (name, price, brand, description, ratings, etc.)
- Handles pagination automatically

✅ **Image Management**
- Downloads product images from the website
- Uploads to AWS S3 with organized folder structure
- Generates S3 paths for reference in Excel files

✅ **Excel Report Generation**
- Creates one Excel file per category
- Separate worksheet for each subcategory
- Includes summary statistics
- Professional formatting with colors and borders
- S3 image path column for easy reference

✅ **S3 Storage with Date Partitioning**
- Organized folder structure: `bucket/boutiqaat-data/year=YYYY/month=MM/day=DD/women-makeup/`
- Separate folders for images and Excel files
- Easy to query and organize data by date

✅ **Automated Scheduling**
- GitHub Actions workflow runs daily
- Configurable schedule (default: 2 AM UTC)
- Manual trigger option available
- Error handling and logging

## Project Structure

```
Project8-Baat/
├── .github/
│   └── workflows/
│       └── scrape-daily.yml          # GitHub Actions workflow
├── src/
│   ├── __init__.py                   # Package initializer
│   ├── scraper.py                    # Web scraper module
│   ├── s3_uploader.py               # S3 upload functions
│   ├── excel_generator.py           # Excel file generation
│   └── main.py                      # Main orchestrator
├── config.py                         # Configuration settings
├── requirements.txt                  # Python dependencies
├── .gitignore                        # Git ignore rules
└── README.md                         # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- AWS Account with S3 access
- GitHub Account (for Actions automation)
- Git

### 2. Local Installation

Clone the repository:
```bash
git clone https://github.com/yourusername/Project8-Baat.git
cd Project8-Baat
```

Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. AWS Setup

#### Create S3 Bucket
```bash
# Using AWS CLI
aws s3 mb s3://your-bucket-name
```

#### Create IAM User
1. Go to AWS IAM Console
2. Create a new user for this pipeline
3. Attach policy with S3 access:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

4. Generate Access Key and Secret Key

### 4. GitHub Setup

#### Add GitHub Secrets

Go to your repository settings → Secrets and variables → Actions, and add:

- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_S3_BUCKET`: Your S3 bucket name (e.g., `your-bucket-name`)

#### Enable GitHub Actions
- Ensure GitHub Actions are enabled in your repository
- The workflow file is already configured

### 5. Local Environment Variables (Optional)

Create a `.env` file for local testing:
```env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET=your-bucket-name
```

Then modify `config.py` to load from .env:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Usage

### Run Locally

```bash
python -m src.main
```

### Run with GitHub Actions

The workflow runs automatically daily at 2 AM UTC. To trigger manually:
1. Go to your GitHub repository
2. Click "Actions" tab
3. Select "Boutiqaat Daily Data Scrape" workflow
4. Click "Run workflow"

### Check Logs

View GitHub Actions logs:
1. Go to Actions tab
2. Click on the completed workflow run
3. View detailed logs

## S3 Folder Structure

```
s3://your-bucket/
└── boutiqaat-data/
    └── year=2026/
        └── month=03/
            └── day=03/
                └── women-makeup/
                    ├── images/
                    │   ├── SKU1_image.jpg
                    │   ├── SKU2_image.jpg
                    │   └── ...
                    ├── Category1_2026-03-03.xlsx
                    ├── Category2_2026-03-03.xlsx
                    └── ...
```

## Excel File Structure

### Summary Sheet
| Subcategory | Product Count | Brands | Average Price |
|---|---|---|---|
| Foundations | 45 | Brand1, Brand2... | 25.50 |

### Category Sheets (one per subcategory)
| Product Name | Brand | Price | SKU | Description | Rating | Reviews | Colors | Product URL | S3 Image Path | Image URL |
|---|---|---|---|---|---|---|---|---|---|---|

## Configuration

Edit `config.py` to customize:

```python
# Schedule (cron format)
# Default: 0 2 * * * (2 AM UTC daily)

# AWS Region
AWS_REGION = 'us-east-1'

# Image settings
IMAGE_QUALITY = 80
MAX_IMAGE_SIZE = (400, 400)

# Request settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2
```

## Monitoring and Troubleshooting

### Common Issues

**S3 Connection Error:**
- Verify AWS credentials
- Check bucket name in GitHub secrets
- Ensure bucket exists and is accessible

**Scraping Errors:**
- Check if website structure has changed
- Verify User-Agent in scraper.py
- Check HTML selectors in scraper.py

**Image Download Issues:**
- Verify image URLs are accessible
- Check internet connection
- Review request timeout settings

### Logging

Logs are created during execution. For GitHub Actions, check:
- Actions tab → Workflow run → Job logs

## Performance Tips

1. **Batch Processing**: The scraper processes categories sequentially to avoid overwhelming the server
2. **Caching**: Consider adding request caching for repeated URLs
3. **Parallelization**: For large-scale scraping, consider using ThreadPoolExecutor

## Advanced Customization

### Add New Data Fields

Edit `src/scraper.py` in `_extract_product_details()` method:
```python
new_field = product_elem.find('selector', class_='class-name')
product_data['new_field'] = new_field.get_text(strip=True) if new_field else 'N/A'
```

### Change Schedule

Edit `.github/workflows/scrape-daily.yml`:
```yaml
cron: '0 2 * * *'  # Change to your preferred time
```

### Add Email Notifications

Use GitHub Actions email notification or integrate with AWS SNS.

## API Reference

### BoutiqaatScraper

```python
scraper = BoutiqaatScraper()

# Get categories
categories = scraper.get_categories()

# Get subcategories
subcategories = scraper.get_subcategories(category_url)

# Get products (with pagination)
products = scraper.get_products(subcategory_url)

# Get full product details
details = scraper.get_product_full_details(product_url)
```

### S3Uploader

```python
uploader = S3Uploader()

# Upload image from URL
s3_path = uploader.upload_image_from_url(image_url, filename)

# Upload local file
s3_path = uploader.upload_local_file(local_path, s3_folder_path)

# Generate presigned URL
url = uploader.generate_presigned_url(s3_key)

# Test connection
uploader.test_connection()
```

### ExcelGenerator

```python
excel_gen = ExcelGenerator()

# Create category workbook
filename = excel_gen.create_category_workbook(category_name, subcategories_data)
```

## Best Practices

1. **Rate Limiting**: The scraper includes delays between requests
2. **Error Handling**: Retry logic for failed requests
3. **Logging**: Comprehensive logging for debugging and monitoring
4. **Data Validation**: Check data before uploading to S3
5. **Testing**: Test locally before deploying to GitHub Actions

## Legal Disclaimer

Ensure you have permission to scrape the target website and comply with:
- Website's robots.txt
- Terms of Service
- Data protection regulations (GDPR, CCPA, etc.)

## Support and Contribution

For issues or improvements:
1. Check GitHub Issues
2. Create a new issue with details
3. Submit pull requests for improvements


## Author

Data Pipeline Team

## Changelog

### v1.0.0 (2026-03-03)
- Initial release
- Web scraper for categories, subcategories, and products
- S3 image upload with date partitioning
- Excel report generation
- GitHub Actions automation
- Full documentation

---

**Last Updated**: 2026-03-03
**Status**: Active
