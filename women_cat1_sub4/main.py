import logging
from typing import Dict, List
import os
import shutil
from datetime import datetime
from collections import defaultdict

from .scraper import BoutiqaatScraper
from .s3_uploader import S3Uploader
from .excel_generator import ExcelGenerator
from config import TEMP_DIR, S3_EXCEL_PATH

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Hardcoded subcategory URLs for Group 4
SUBCATEGORY_URLS = [
    "https://www.boutiqaat.com/ar-kw/women/makeup/lash-and-brow-regrowth/l/",
    "https://www.boutiqaat.com/ar-kw/women/makeup/false-eyelashes/l/",
    "https://www.boutiqaat.com/ar-kw/women/makeup/eyelash-adhesive/l/",
    "https://www.boutiqaat.com/ar-kw/women/makeup/makeup-brushes/l/",
    "https://www.boutiqaat.com/ar-kw/women/makeup/makeup-sponges/l/",
    "https://www.boutiqaat.com/ar-kw/women/makeup/tweezers-sharpeners/l/",
    "https://www.boutiqaat.com/ar-kw/women/makeup/eyelash-curlers/l/",
    "https://www.boutiqaat.com/ar-kw/women/makeup/brush-sets/l/",
]


class BoutiqaatDataPipeline:
    """Main orchestrator for scraping, processing, and uploading data"""

    def __init__(self):
        self.scraper = BoutiqaatScraper()
        self.uploader = S3Uploader()
        self.excel_generator = ExcelGenerator()

    def run(self):
        """Execute the complete data pipeline sequentially"""
        logger.info("=" * 80)
        logger.info("Starting Boutiqaat Data Pipeline - Group 4 (Sequential)")
        logger.info("=" * 80)
        
        try:
            # Test S3 connection
            if not self.uploader.test_connection():
                logger.error("S3 connection failed. Exiting.")
                return False
            
            logger.info(f"Processing {len(SUBCATEGORY_URLS)} subcategories sequentially")
            
            successful = 0
            failed = 0
            
            for url in SUBCATEGORY_URLS:
                # Extract category name from URL
                category_name = url.rstrip('/').split('/')[-2]
                category_dict = {'name': category_name, 'url': url}
                
                try:
                    result = self._process_category(category_dict)
                    if result:
                        successful += 1
                    else:
                        failed += 1
                except Exception as e:
                    logger.error(f"Exception processing {category_name}: {str(e)}")
                    failed += 1
            
            logger.info("=" * 80)
            logger.info(f"Pipeline completed: {successful} successful, {failed} failed")
            logger.info("=" * 80)
            return True
        
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            return False
        finally:
            if os.path.exists(TEMP_DIR):
                try:
                    shutil.rmtree(TEMP_DIR)
                    logger.info("Cleaned up temporary files")
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp files: {e}")

    def _process_category(self, category: Dict) -> bool:
        """Process a single category and extract products"""
        category_name = category['name']
        category_url = category['url']
        
        logger.info(f"\n--- Processing Category: {category_name} ---")
        
        try:
            products = self.scraper.get_products(category_url)
            
            if not products:
                logger.warning(f"No products found for {category_name}")
                return False
            
            logger.info(f"Found {len(products)} total products in category")
            
            subcategories_data = defaultdict(list)
            
            for product in products:
                subcategory = product.get('subcategory', category_name)
                subcategories_data[subcategory].append(product)
            
            for subcategory_name, products_in_sub in subcategories_data.items():
                logger.info(f"  Processing Subcategory: {subcategory_name} ({len(products_in_sub)} products)")
                
                for idx, product in enumerate(products_in_sub, 1):
                    logger.info(f"    [{idx}/{len(products_in_sub)}] Processing: {product.get('name', 'Unknown')}")
                    
                    try:
                        full_details = self.scraper.get_product_full_details(product['url'])
                        if full_details:
                            product.update(full_details)
                        
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
            
            if subcategories_data:
                excel_file = self.excel_generator.create_category_workbook(
                    category_name,
                    subcategories_data
                )
                
                self._upload_excel_file(excel_file, category_name)
            
            logger.info(f"✓ Completed category: {category_name}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed category {category_name}: {str(e)}")
            return False

    def _upload_product_image(self, product: Dict, category_name: str, subcategory_name: str) -> str:
        """Download and upload product image to S3"""
        try:
            image_url = product.get('image_url')
            sku = product.get('sku', 'unknown')
            
            if not image_url:
                return 'No image URL'
            
            # Sanitize names for S3 path
            safe_category = "".join(c for c in category_name if c.isalnum() or c in (' ', '_')).rstrip()
            
            # S3 path: boutiqaat-data/year=YYYY/month=MM/day=DD/women-makeup/images/category/
            s3_path = (
                f"boutiqaat-data/year={datetime.now().strftime('%Y')}/month={datetime.now().strftime('%m')}/day={datetime.now().strftime('%d')}/women-makeup/images/"
                f"{safe_category}"
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
            
            # S3 path: boutiqaat-data/year=YYYY/month=MM/day=DD/women-makeup/excel-files/
            s3_path = (
                f"boutiqaat-data/year={datetime.now().strftime('%Y')}/month={datetime.now().strftime('%m')}/day={datetime.now().strftime('%d')}/women-makeup/excel-files"
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
