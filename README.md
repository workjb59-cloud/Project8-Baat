# Boutiqaat Scraper

Comprehensive web scraper for Boutiqaat.com that extracts product data from categories, brands, and celebrities, downloads images, and stores everything in AWS S3 with organized Excel files.

## Features

✅ **Multi-Source Scraping**: Extract products from:
- Categories (e.g., Foundations, Lipsticks)
- Brands (e.g., MAC, NARS)
- Celebrities (e.g., Kylie Jenner)

✅ **Using Scrapling Library**: Modern web scraping with automatic matching

✅ **Image Processing**: 
- Download product images
- Optimize image sizes
- Upload to S3

✅ **Excel Export**:
- Celebrities: One file per celebrity
- Brands: One file with all brands as sheets
- Categories: One file per main category with subcategories as sheets

✅ **S3 Organization**: Partitioned by date
```
boutiqaat-data/
└── year=2026/
    └── month=02/
        └── day=28/
            ├── categories/
            │   ├── excel_files/
            │   └── images/
            ├── brands/
            │   ├── excel_files/
            │   └── images/
            └── celebrities/
                ├── excel_files/
                └── images/
```

## Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Project8-Baat
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your AWS credentials
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key
# S3_BUCKET_NAME=boutiqaat-data
```

## Usage

### Basic Usage

Run the complete pipeline with sample data:

```bash
python main.py
```

### Custom Scraping

Edit `main.py` to customize what you want to scrape:

```python
from main import BoutiqaatPipeline

pipeline = BoutiqaatPipeline()

# Define your targets
categories = [
    {'name': 'Foundations', 'slug': 'makeup/foundations/l'},
    {'name': 'Lipsticks', 'slug': 'makeup/lipstick/l'},
]

brands = [
    {'name': 'MAC', 'slug': 'mac'},
    {'name': 'NARS', 'slug': 'nars'},
]

celebrities = [
    {'name': 'Kylie Jenner', 'slug': 'kylie-jenner'},
]

# Run pipeline
results = pipeline.run_full_pipeline(
    categories=categories,
    brands=brands,
    celebrities=celebrities
)
```

### Individual Components

You can use individual components separately:

**Scraper Only:**
```python
from scraper import BoutiqaatScraper

scraper = BoutiqaatScraper()
products = scraper.scrape_category('makeup/foundations/l')
print(f"Found {len(products)} products")
```

**Excel Export Only:**
```python
from excel_exporter import ExcelExporter

exporter = ExcelExporter()
excel_files = exporter.export_celebrities_to_excel(celebrities_data)
```

**Image Download Only:**
```python
from image_downloader import ImageDownloader

downloader = ImageDownloader()
result = downloader.download_and_upload_image(
    image_url="https://example.com/image.jpg",
    product_sku="SKU-001",
    s3_path="boutiqaat-data/images"
)
```

## Project Structure

```
Project8-Baat/
├── config.py              # Configuration and settings
├── scraper.py             # Scrapling-based web scraper
├── excel_exporter.py      # Excel file generation
├── image_downloader.py    # Image processing and S3 upload
├── main.py                # Main orchestrator
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `AWS_ACCESS_KEY_ID` | AWS access key | Yes | - |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Yes | - |
| `AWS_REGION` | AWS region | No | `us-east-1` |
| `S3_BUCKET_NAME` | S3 bucket name | No | `boutiqaat-data` |
| `LOG_LEVEL` | Logging level | No | `INFO` |

### Scraping Settings

Edit `config.py` to adjust:
- Request timeout
- Max retries
- Retry delays
- Excel column mappings
- S3 path structure

## Output

### Excel Files

**Product Columns:**
- entity_id, sku, name, short_description
- brand_id, brand_name
- category_id, category_name
- regular_price, final_price, discount_percentage, currency_code
- image_url, product_url
- product_type, is_saleable
- qty_available, qty_allowed
- exclusive, exclusive_celebrity
- gender, track_name, track_category, track_brand
- ad_number, category_tree
- related_products_count, scraped_at

### S3 Structure

All files are uploaded to S3 with the following structure:

```
s3://boutiqaat-data/year=YYYY/month=MM/day=DD/
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

## Logging

Logs are written to:
- Console (stdout)
- `boutiqaat_scraper.log` file

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Error Handling

- Automatic retries for failed requests
- Graceful handling of missing data
- Detailed error logging
- Results JSON includes error summaries

## Performance Tips

1. **Rate Limiting**: The scraper includes 1-second delays between requests
2. **Image Optimization**: Images are optimized to reduce storage costs
3. **Batch Processing**: Excel files and images are processed in batches
4. **Progress Tracking**: tqdm progress bars show real-time progress

## Troubleshooting

### Common Issues

**1. AWS Credentials Error**
```
Error: Unable to locate credentials
```
Solution: Ensure `.env` file exists with valid AWS credentials

**2. S3 Bucket Not Found**
```
Error: Bucket does not exist
```
Solution: The script will automatically create the bucket if it doesn't exist

**3. Scraping Timeouts**
```
Error: Request timed out
```
Solution: Increase `REQUEST_TIMEOUT` in `config.py`

**4. Missing Dependencies**
```
ModuleNotFoundError: No module named 'scrapling'
```
Solution: Run `pip install -r requirements.txt`

## Dependencies

- **scrapling** - Modern web scraping library
- **boto3** - AWS SDK for Python
- **pandas** - Data manipulation
- **openpyxl** - Excel file creation
- **Pillow** - Image processing
- **python-dotenv** - Environment variable management
- **tqdm** - Progress bars
- **requests** - HTTP library
- **beautifulsoup4** - HTML parsing
- **lxml** - XML/HTML parser

## License

This project is for educational and personal use only. Please respect Boutiqaat's terms of service and robots.txt when scraping.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions:
- Check the logs in `boutiqaat_scraper.log`
- Review the results JSON file
- Open an issue on GitHub

## Roadmap

- [ ] Add support for pagination
- [ ] Implement concurrent scraping
- [ ] Add database storage option
- [ ] Create API endpoint
- [ ] Add scheduling support
- [ ] Export to additional formats (CSV, JSON)
- [ ] Add data validation and cleaning
- [ ] Implement change detection

## Author

Created for efficient Boutiqaat product data collection and organization.

## Acknowledgments

- Built with [Scrapling](https://scrapling.readthedocs.io/) library
- Uses AWS S3 for storage
- Organized Excel exports with openpyxl
