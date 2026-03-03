import logging
from typing import Dict, List
from collections import defaultdict
import os
import shutil
from datetime import datetime

from .scraper import BoutiqaatScraper
from .s3_uploader import S3Uploader
from .excel_generator import ExcelGenerator
from config import TEMP_DIR, S3_EXCEL_PATH

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BoutiqaatDataPipeline:
    """Main orchestrator for scraping, processing, and uploading data"""

    def __init__(self):
        self.scraper = BoutiqaatScraper()
        self.uploader = S3Uploader()
        self.excel_generator = ExcelGenerator()

    def run(self):
        """Execute the complete data pipeline"""
        logger.info("=" * 80)
        logger.info("Starting Boutiqaat Data Pipeline")
        logger.info("=" * 80)
        
        try:
            # Test S3 connection
            if not self.uploader.test_connection():
                logger.error("S3 connection failed. Exiting.")
                return False
            
            # Scrape categories
            categories = self.scraper.get_categories()
            if not categories:
                logger.error("No categories found")
                return False
            
            logger.info(f"Processing {len(categories)} categories")
            
            # Process each category
            for category in categories:
                self._process_category(category)
            
            logger.info("=" * 80)
            logger.info("Pipeline completed successfully")
            logger.info("=" * 80)
            return True
        
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            return False
        finally:
            # Cleanup temp directory
            if os.path.exists(TEMP_DIR):
                shutil.rmtree(TEMP_DIR)
                logger.info("Cleaned up temporary files")

    def _process_category(self, category: Dict):
        """Process a single category and all its subcategories"""
        category_name = category['name']
        category_url = category['url']
        
        logger.info(f"\n--- Processing Category: {category_name} ---")
        
        # Get subcategories
        subcategories = self.scraper.get_subcategories(category_url)
        if not subcategories:
            logger.warning(f"No subcategories found for {category_name}")
            return
        
        # Organize products by subcategory
        subcategories_data = defaultdict(list)
        
        for subcategory in subcategories:
            subcategory_name = subcategory['name']
            subcategory_url = subcategory['url']
            
            logger.info(f"  Processing Subcategory: {subcategory_name}")
            
            # Get products in subcategory
            products = self.scraper.get_products(subcategory_url)
            
            if not products:
                logger.warning(f"    No products found")
                continue
            
            logger.info(f"    Found {len(products)} products")
            
            # Process each product
            for idx, product in enumerate(products, 1):
                logger.info(f"    [{idx}/{len(products)}] Processing: {product.get('name', 'Unknown')}")
                
                # Get full product details
                full_details = self.scraper.get_product_full_details(product['url'])
                if full_details:
                    product.update(full_details)
                
                # Download and upload image
                if product.get('image_url'):
                    s3_image_path = self._upload_product_image(product)
                    product['s3_image_path'] = s3_image_path
                else:
                    product['s3_image_path'] = 'No image available'
                
                subcategories_data[subcategory_name].append(product)
        
        # Generate Excel file
        if subcategories_data:
            excel_file = self.excel_generator.create_category_workbook(
                category_name,
                subcategories_data
            )
            
            # Upload Excel to S3
            self._upload_excel_file(excel_file, category_name)

    def _upload_product_image(self, product: Dict) -> str:
        """Download and upload product image to S3"""
        try:
            image_url = product.get('image_url')
            sku = product.get('sku', 'unknown')
            
            if not image_url:
                return 'No image URL'
            
            # Generate filename
            filename = f"{sku}_image.jpg"
            
            # Upload image
            s3_path = self.uploader.upload_image_from_url(
                image_url,
                filename
            )
            
            return s3_path if s3_path else 'Upload failed'
        
        except Exception as e:
            logger.warning(f"Error uploading image for {product.get('name')}: {str(e)}")
            return 'Error'

    def _upload_excel_file(self, local_path: str, category_name: str) -> bool:
        """Upload Excel file to S3"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{category_name}_{timestamp}.xlsx"
            
            s3_path = self.uploader.upload_local_file(
                local_path,
                S3_EXCEL_PATH,
                filename
            )
            
            if s3_path:
                logger.info(f"Excel file uploaded: {s3_path}")
                return True
            else:
                logger.error(f"Failed to upload Excel file: {local_path}")
                return False
        
        except Exception as e:
            logger.error(f"Error uploading Excel file: {str(e)}")
            return False


def main():
    """Entry point for the pipeline"""
    pipeline = BoutiqaatDataPipeline()
    success = pipeline.run()
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
