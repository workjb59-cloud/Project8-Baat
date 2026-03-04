import logging
from typing import Dict, List
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
        """Process a single category and extract products by subcategory"""
        category_name = category['name']
        category_url = category['url']
        
        logger.info(f"\n--- Processing Category: {category_name} ---")
        
        # Get the category page to extract products and subcategories
        products = self.scraper.get_products(category_url)
        
        if not products:
            logger.warning(f"No products found for {category_name}")
            return
        
        logger.info(f"Found {len(products)} total products in category")
        
        # Organize products by their subcategory (extracted from product details or page structure)
        from collections import defaultdict
        subcategories_data = defaultdict(list)
        
        # If products don't have subcategory info, group them under category name
        for product in products:
            # Try to get subcategory from product or use category name as default
            subcategory = product.get('subcategory', category_name)
            subcategories_data[subcategory].append(product)
        
        # Process each product to get full details and upload images
        for subcategory_name, products_in_sub in subcategories_data.items():
            logger.info(f"  Processing Subcategory: {subcategory_name} ({len(products_in_sub)} products)")
            
            for idx, product in enumerate(products_in_sub, 1):
                logger.info(f"    [{idx}/{len(products_in_sub)}] Processing: {product.get('name', 'Unknown')}")
                
                try:
                    # Get full product details
                    full_details = self.scraper.get_product_full_details(product['url'])
                    if full_details:
                        product.update(full_details)
                    
                    # Download and upload image
                    if product.get('image_url'):
                        s3_image_path = self._upload_product_image(
                            product,
                            category_name,
                            subcategory_name
                        )
                        product['s3_image_path'] = s3_image_path
                    else:
                        product['s3_image_path'] = 'No image available'
                
                except Exception as e:
                    logger.warning(f"    Error processing product: {str(e)}")
                    continue
        
        # Generate Excel file with subcategories as sheets
        if subcategories_data:
            excel_file = self.excel_generator.create_category_workbook(
                category_name,
                subcategories_data
            )
            
            # Upload Excel to S3
            self._upload_excel_file(excel_file, category_name)

    def _upload_product_image(self, product: Dict, category_name: str, subcategory_name: str) -> str:
        """Download and upload product image to S3"""
        try:
            image_url = product.get('image_url')
            sku = product.get('sku', 'unknown')
            
            if not image_url:
                return 'No image URL'
            
            # Sanitize names for S3 path
            safe_category = "".join(c for c in category_name if c.isalnum() or c in (' ', '_')).rstrip()
            safe_subcategory = "".join(c for c in subcategory_name if c.isalnum() or c in (' ', '_')).rstrip()
            
            # S3 path: year=YYYY/month=MM/day=DD/women-makeup/images/category/subcategory/
            s3_path = (
                f"year={datetime.now().strftime('%Y')}/month={datetime.now().strftime('%m')}/day={datetime.now().strftime('%d')}/women-makeup/images/"
                f"{safe_category}/{safe_subcategory}"
            )
            
            # Generate filename
            filename = f"{sku}_image.jpg"
            
            # Upload image
            s3_key = self.uploader.upload_image_from_url(
                image_url,
                filename,
                s3_path
            )
            
            return s3_key if s3_key else 'Upload failed'
        
        except Exception as e:
            logger.warning(f"Error uploading image for {product.get('name')}: {str(e)}")
            return 'Error'

    def _upload_excel_file(self, local_path: str, category_name: str) -> bool:
        """Upload Excel file to S3"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{category_name}_{timestamp}.xlsx"
            
            # S3 path: year=YYYY/month=MM/day=DD/women-makeup/excel-files/
            s3_path = (
                f"year={datetime.now().strftime('%Y')}/month={datetime.now().strftime('%m')}/day={datetime.now().strftime('%d')}/women-makeup/excel-files"
            )
            
            s3_key = self.uploader.upload_local_file(
                local_path,
                s3_path,
                filename
            )
            
            if s3_key:
                logger.info(f"Excel file uploaded: {s3_key}")
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
