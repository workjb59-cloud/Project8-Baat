"""
Main orchestrator for Boutiqaat scraper
Coordinates scraping, image downloading, Excel generation, and S3 uploads
"""
import logging
import json
from datetime import datetime
from typing import Dict, List
import config
from scraper import BoutiqaatScraper
from excel_exporter import ExcelExporter
from image_downloader import ImageDownloader

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BoutiqaatPipeline:
    """Main pipeline for scraping and processing Boutiqaat data"""
    
    def __init__(self):
        """Initialize all components"""
        logger.info("Initializing Boutiqaat Pipeline...")
        self.scraper = BoutiqaatScraper()
        self.exporter = ExcelExporter()
        self.downloader = ImageDownloader()
        logger.info("Pipeline initialized successfully")
    
    def process_celebrities(self, celebrities: List[Dict]) -> Dict:
        """
        Process celebrities: scrape, download images, create Excel, upload to S3
        
        Args:
            celebrities: List of dicts with 'name' and 'slug' keys
            
        Returns:
            Dict with processing results
        """
        logger.info("=" * 80)
        logger.info("PROCESSING CELEBRITIES")
        logger.info("=" * 80)
        
        results = {
            'celebrities_count': len(celebrities),
            'products_scraped': 0,
            'images_downloaded': 0,
            'excel_files_uploaded': 0,
            'excel_urls': {},
            'errors': []
        }
        
        try:
            # Step 1: Scrape products
            logger.info(f"Step 1/4: Scraping {len(celebrities)} celebrities...")
            celebrities_data = self.scraper.scrape_celebrities(celebrities)
            
            if not celebrities_data:
                logger.warning("No data scraped for celebrities")
                return results
            
            # Count products
            total_products = sum(len(products) for products in celebrities_data.values())
            results['products_scraped'] = total_products
            logger.info(f"Scraped {total_products} products from {len(celebrities_data)} celebrities")
            
            # Step 2: Download images for each celebrity
            logger.info("Step 2/4: Downloading and uploading images to S3...")
            for celebrity_name, products in celebrities_data.items():
                if products:
                    s3_images_path = f"{config.CELEBRITIES_IMAGES_PATH}/{self._clean_path(celebrity_name)}"
                    celebrities_data[celebrity_name] = self.downloader.process_products_images(
                        products, s3_images_path
                    )
                    results['images_downloaded'] += len(products)
            
            logger.info(f"Processed images for {results['images_downloaded']} products")
            
            # Step 3: Generate Excel files
            logger.info("Step 3/4: Generating Excel files...")
            excel_files = self.exporter.export_celebrities_to_excel(celebrities_data)
            logger.info(f"Generated {len(excel_files)} Excel files")
            
            # Step 4: Upload Excel files to S3
            logger.info("Step 4/4: Uploading Excel files to S3...")
            uploaded_files = self.downloader.batch_upload_excel_files(
                excel_files, config.CELEBRITIES_EXCEL_PATH
            )
            results['excel_files_uploaded'] = len(uploaded_files)
            results['excel_urls'] = uploaded_files
            
            logger.info(f"Successfully uploaded {len(uploaded_files)} Excel files")
            
        except Exception as e:
            logger.error(f"Error processing celebrities: {e}", exc_info=True)
            results['errors'].append(str(e))
        
        return results
    
    def process_brands(self, brands: List[Dict]) -> Dict:
        """
        Process brands: scrape, download images, create Excel, upload to S3
        
        Args:
            brands: List of dicts with 'name' and 'slug' keys
            
        Returns:
            Dict with processing results
        """
        logger.info("=" * 80)
        logger.info("PROCESSING BRANDS")
        logger.info("=" * 80)
        
        results = {
            'brands_count': len(brands),
            'products_scraped': 0,
            'images_downloaded': 0,
            'excel_files_uploaded': 0,
            'excel_urls': {},
            'errors': []
        }
        
        try:
            # Step 1: Scrape products
            logger.info(f"Step 1/4: Scraping {len(brands)} brands...")
            brands_data = self.scraper.scrape_brands(brands)
            
            if not brands_data:
                logger.warning("No data scraped for brands")
                return results
            
            # Count products
            total_products = sum(len(products) for products in brands_data.values())
            results['products_scraped'] = total_products
            logger.info(f"Scraped {total_products} products from {len(brands_data)} brands")
            
            # Step 2: Download images for each brand
            logger.info("Step 2/4: Downloading and uploading images to S3...")
            for brand_name, products in brands_data.items():
                if products:
                    s3_images_path = f"{config.BRANDS_IMAGES_PATH}/{self._clean_path(brand_name)}"
                    brands_data[brand_name] = self.downloader.process_products_images(
                        products, s3_images_path
                    )
                    results['images_downloaded'] += len(products)
            
            logger.info(f"Processed images for {results['images_downloaded']} products")
            
            # Step 3: Generate Excel file (single file with all brands)
            logger.info("Step 3/4: Generating Excel file with all brands...")
            excel_files = self.exporter.export_brands_to_excel(brands_data)
            logger.info(f"Generated Excel file with {len(brands_data)} brand sheets")
            
            # Step 4: Upload Excel file to S3
            logger.info("Step 4/4: Uploading Excel file to S3...")
            uploaded_files = self.downloader.batch_upload_excel_files(
                excel_files, config.BRANDS_EXCEL_PATH
            )
            results['excel_files_uploaded'] = len(uploaded_files)
            results['excel_urls'] = uploaded_files
            
            logger.info(f"Successfully uploaded Excel file")
            
        except Exception as e:
            logger.error(f"Error processing brands: {e}", exc_info=True)
            results['errors'].append(str(e))
        
        return results
    
    def process_categories(self, categories: List[Dict]) -> Dict:
        """
        Process categories: scrape, download images, create Excel, upload to S3
        
        Args:
            categories: List of dicts with 'name' and 'slug' keys
            
        Returns:
            Dict with processing results
        """
        logger.info("=" * 80)
        logger.info("PROCESSING CATEGORIES")
        logger.info("=" * 80)
        
        results = {
            'categories_count': len(categories),
            'products_scraped': 0,
            'images_downloaded': 0,
            'excel_files_uploaded': 0,
            'excel_urls': {},
            'errors': []
        }
        
        try:
            # Step 1: Scrape products
            logger.info(f"Step 1/4: Scraping {len(categories)} categories...")
            categories_data = self.scraper.scrape_categories(categories)
            
            if not categories_data:
                logger.warning("No data scraped for categories")
                return results
            
            # Count products
            total_products = sum(len(products) for products in categories_data.values())
            results['products_scraped'] = total_products
            logger.info(f"Scraped {total_products} products from {len(categories_data)} categories")
            
            # Step 2: Download images for each category
            logger.info("Step 2/4: Downloading and uploading images to S3...")
            for category_name, products in categories_data.items():
                if products:
                    s3_images_path = f"{config.CATEGORIES_IMAGES_PATH}/{self._clean_path(category_name)}"
                    categories_data[category_name] = self.downloader.process_products_images(
                        products, s3_images_path
                    )
                    results['images_downloaded'] += len(products)
            
            logger.info(f"Processed images for {results['images_downloaded']} products")
            
            # Step 3: Generate Excel files (one per main category, subcategories as sheets)
            logger.info("Step 3/4: Generating Excel files...")
            excel_files = self.exporter.export_categories_to_excel(categories_data)
            logger.info(f"Generated {len(excel_files)} Excel files")
            
            # Step 4: Upload Excel files to S3
            logger.info("Step 4/4: Uploading Excel files to S3...")
            uploaded_files = self.downloader.batch_upload_excel_files(
                excel_files, config.CATEGORIES_EXCEL_PATH
            )
            results['excel_files_uploaded'] = len(uploaded_files)
            results['excel_urls'] = uploaded_files
            
            logger.info(f"Successfully uploaded {len(uploaded_files)} Excel files")
            
        except Exception as e:
            logger.error(f"Error processing categories: {e}", exc_info=True)
            results['errors'].append(str(e))
        
        return results
    
    def run_full_pipeline(self, categories: List[Dict], brands: List[Dict], celebrities: List[Dict]) -> Dict:
        """
        Run the complete pipeline for all data types
        
        Args:
            categories: List of category dicts
            brands: List of brand dicts
            celebrities: List of celebrity dicts
            
        Returns:
            Dict with complete results
        """
        start_time = datetime.now()
        logger.info("=" * 80)
        logger.info("STARTING FULL BOUTIQAAT SCRAPING PIPELINE")
        logger.info(f"Start Time: {start_time}")
        logger.info("=" * 80)
        
        results = {
            'start_time': start_time.isoformat(),
            'categories_results': {},
            'brands_results': {},
            'celebrities_results': {},
            'end_time': None,
            'duration_seconds': None
        }
        
        # Process each data type
        if categories:
            results['categories_results'] = self.process_categories(categories)
        
        if brands:
            results['brands_results'] = self.process_brands(brands)
        
        if celebrities:
            results['celebrities_results'] = self.process_celebrities(celebrities)
        
        # Calculate duration
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        results['end_time'] = end_time.isoformat()
        results['duration_seconds'] = duration
        
        logger.info("=" * 80)
        logger.info("PIPELINE COMPLETED")
        logger.info(f"End Time: {end_time}")
        logger.info(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
        logger.info("=" * 80)
        
        # Save results to JSON
        results_file = f"pipeline_results_{config.YEAR}{config.MONTH}{config.DAY}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to: {results_file}")
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def _clean_path(self, name: str) -> str:
        """Clean name for use in S3 path"""
        # Replace spaces and special characters
        cleaned = name.replace(' ', '_').replace('/', '_')
        # Remove other invalid characters
        invalid_chars = '<>:"|?*'
        for char in invalid_chars:
            cleaned = cleaned.replace(char, '_')
        return cleaned.lower()
    
    def _print_summary(self, results: Dict):
        """Print a summary of the pipeline results"""
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE SUMMARY")
        logger.info("=" * 80)
        
        # Categories summary
        if results.get('categories_results'):
            cat_res = results['categories_results']
            logger.info(f"\nCATEGORIES:")
            logger.info(f"  - Categories processed: {cat_res.get('categories_count', 0)}")
            logger.info(f"  - Products scraped: {cat_res.get('products_scraped', 0)}")
            logger.info(f"  - Images downloaded: {cat_res.get('images_downloaded', 0)}")
            logger.info(f"  - Excel files uploaded: {cat_res.get('excel_files_uploaded', 0)}")
            if cat_res.get('errors'):
                logger.info(f"  - Errors: {len(cat_res['errors'])}")
        
        # Brands summary
        if results.get('brands_results'):
            brand_res = results['brands_results']
            logger.info(f"\nBRANDS:")
            logger.info(f"  - Brands processed: {brand_res.get('brands_count', 0)}")
            logger.info(f"  - Products scraped: {brand_res.get('products_scraped', 0)}")
            logger.info(f"  - Images downloaded: {brand_res.get('images_downloaded', 0)}")
            logger.info(f"  - Excel files uploaded: {brand_res.get('excel_files_uploaded', 0)}")
            if brand_res.get('errors'):
                logger.info(f"  - Errors: {len(brand_res['errors'])}")
        
        # Celebrities summary
        if results.get('celebrities_results'):
            celeb_res = results['celebrities_results']
            logger.info(f"\nCELEBRITIES:")
            logger.info(f"  - Celebrities processed: {celeb_res.get('celebrities_count', 0)}")
            logger.info(f"  - Products scraped: {celeb_res.get('products_scraped', 0)}")
            logger.info(f"  - Images downloaded: {celeb_res.get('images_downloaded', 0)}")
            logger.info(f"  - Excel files uploaded: {celeb_res.get('excel_files_uploaded', 0)}")
            if celeb_res.get('errors'):
                logger.info(f"  - Errors: {len(celeb_res['errors'])}")
        
        # Total summary
        total_products = (
            results.get('categories_results', {}).get('products_scraped', 0) +
            results.get('brands_results', {}).get('products_scraped', 0) +
            results.get('celebrities_results', {}).get('products_scraped', 0)
        )
        total_images = (
            results.get('categories_results', {}).get('images_downloaded', 0) +
            results.get('brands_results', {}).get('images_downloaded', 0) +
            results.get('celebrities_results', {}).get('images_downloaded', 0)
        )
        total_excel = (
            results.get('categories_results', {}).get('excel_files_uploaded', 0) +
            results.get('brands_results', {}).get('excel_files_uploaded', 0) +
            results.get('celebrities_results', {}).get('excel_files_uploaded', 0)
        )
        
        logger.info(f"\nTOTAL:")
        logger.info(f"  - Total products scraped: {total_products}")
        logger.info(f"  - Total images downloaded: {total_images}")
        logger.info(f"  - Total Excel files uploaded: {total_excel}")
        logger.info(f"  - Duration: {results.get('duration_seconds', 0):.2f} seconds")
        logger.info("=" * 80 + "\n")


def validate_environment():
    """
    Validate required environment variables before starting
    """
    required_vars = {
        'AWS_ACCESS_KEY_ID': config.AWS_ACCESS_KEY_ID,
        'AWS_SECRET_ACCESS_KEY': config.AWS_SECRET_ACCESS_KEY,
        'S3_BUCKET_NAME': config.S3_BUCKET_NAME
    }
    
    missing = []
    for var_name, var_value in required_vars.items():
        if not var_value:
            missing.append(var_name)
    
    if missing:
        error_msg = f"Missing required environment variables: {', '.join(missing)}\n"
        error_msg += "\nPlease set these in GitHub Actions secrets or in your .env file:\n"
        error_msg += "  - AWS_ACCESS_KEY_ID\n"
        error_msg += "  - AWS_SECRET_ACCESS_KEY\n"
        error_msg += "  - S3_BUCKET_NAME\n"
        error_msg += "\nFor GitHub Actions: Settings → Secrets and variables → Actions\n"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info(f"Environment validated. Using region: {config.AWS_REGION}, bucket: {config.S3_BUCKET_NAME}")


def main():
    """Main entry point"""
    # Validate environment variables first
    try:
        validate_environment()
    except ValueError as e:
        logger.error(f"Environment validation failed: {e}")
        return
    
    # Initialize pipeline
    pipeline = BoutiqaatPipeline()
    
    # Import configuration
    try:
        from scraping_config import get_categories, get_brands, get_celebrities
        
        categories = get_categories()
        brands = get_brands()
        celebrities = get_celebrities()
        
        logger.info(f"Loaded configuration: {len(categories)} categories, {len(brands)} brands, {len(celebrities)} celebrities")
        
        # Validate categories have category_url
        if categories:
            missing_url = [cat.get('name', 'unknown') for cat in categories if not cat.get('category_url')]
            if missing_url:
                logger.warning(f"⚠️  {len(missing_url)} categories are missing 'category_url' and will be SKIPPED:")
                for name in missing_url[:5]:  # Show first 5
                    logger.warning(f"   - {name}")
                logger.warning("   Run 'python discover_categories.py' to get correct URLs")
        else:
            logger.warning("⚠️  No categories configured in scraping_config.py")
            logger.warning("   Run 'python discover_categories.py' to discover categories")
        
    except ImportError:
        logger.warning("scraping_config.py not found. Using sample data.")
        # Fallback to sample data
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
    
    # Run the pipeline
    results = pipeline.run_full_pipeline(
        categories=categories,
        brands=brands,
        celebrities=celebrities
    )
    
    return results


if __name__ == '__main__':
    main()
