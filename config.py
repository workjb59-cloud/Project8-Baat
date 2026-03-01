"""
Configuration settings for Boutiqaat scraper
Works with both GitHub Actions secrets and local .env file
"""
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env if it exists (for local development)
# In GitHub Actions, variables come from secrets
load_dotenv()

# S3 Configuration (from GitHub Actions secrets or .env file)
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
# AWS Region is hardcoded (change if needed)
AWS_REGION = 'us-east-1'
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME') or 'boutiqaat-data'

# Date partitioning
CURRENT_DATE = datetime.now()
YEAR = CURRENT_DATE.strftime('%Y')
MONTH = CURRENT_DATE.strftime('%m')
DAY = CURRENT_DATE.strftime('%d')

# S3 Path structure
BASE_S3_PATH = f"boutiqaat-data/year={YEAR}/month={MONTH}/day={DAY}"

# Categories
CATEGORIES_PATH = f"{BASE_S3_PATH}/categories"
CATEGORIES_EXCEL_PATH = f"{CATEGORIES_PATH}/excel_files"
CATEGORIES_IMAGES_PATH = f"{CATEGORIES_PATH}/images"

# Brands
BRANDS_PATH = f"{BASE_S3_PATH}/brands"
BRANDS_EXCEL_PATH = f"{BRANDS_PATH}/excel_files"
BRANDS_IMAGES_PATH = f"{BRANDS_PATH}/images"

# Celebrities
CELEBRITIES_PATH = f"{BASE_S3_PATH}/celebrities"
CELEBRITIES_EXCEL_PATH = f"{CELEBRITIES_PATH}/excel_files"
CELEBRITIES_IMAGES_PATH = f"{CELEBRITIES_PATH}/images"

# Boutiqaat URLs
BASE_URL = "https://www.boutiqaat.com"
BASE_URL_AR_KW = f"{BASE_URL}/ar-kw/women"

# Scraping Configuration
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0',
}

# Request settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2

# Scrapling settings
SCRAPLING_AUTO_MATCH = True
SCRAPLING_TIMEOUT = 30

# Excel column mapping
PRODUCT_COLUMNS = [
    'entity_id',
    'sku',
    'name',
    'short_description',
    'brand_id',
    'brand_name',
    'category_id',
    'category_name',
    'regular_price',
    'final_price',
    'discount_percentage',
    'currency_code',
    'image_url',
    'product_url',
    'product_type',
    'is_saleable',
    'qty_available',
    'qty_allowed',
    'exclusive',
    'exclusive_celebrity',
    'gender',
    'track_name',
    'track_category',
    'track_brand',
    'ad_number',
    'category_tree',
    'related_products_count',
    'scraped_at'
]

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = 'boutiqaat_scraper.log'

# Local cache directory (optional)
LOCAL_CACHE_DIR = './cache'
os.makedirs(LOCAL_CACHE_DIR, exist_ok=True)
