"""
Image Downloader and S3 Uploader for Boutiqaat products
Downloads product images and uploads to S3
"""
import os
import io
import hashlib
import requests
from urllib.parse import urlparse
from typing import List, Dict, Set
import boto3
from botocore.exceptions import ClientError
from PIL import Image
from tqdm import tqdm
import logging
import config

logger = logging.getLogger(__name__)


class ImageDownloader:
    """Download product images and upload to S3"""
    
    def __init__(self):
        """Initialize the image downloader with S3 client"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
                region_name=config.AWS_REGION
            )
            self.bucket_name = config.S3_BUCKET_NAME
            self._verify_bucket()
        except Exception as e:
            logger.error(f"Error initializing S3 client: {e}")
            raise
    
    def _verify_bucket(self):
        """Verify that the S3 bucket exists and is accessible"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Successfully connected to S3 bucket: {self.bucket_name}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.warning(f"Bucket {self.bucket_name} does not exist. Creating it...")
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Created bucket: {self.bucket_name}")
                except Exception as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    raise
            else:
                logger.error(f"Error accessing bucket: {e}")
                raise
    
    def download_image(self, image_url: str) -> bytes:
        """Download image from URL"""
        try:
            response = requests.get(image_url, headers=config.HEADERS, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Error downloading image {image_url}: {e}")
            return None
    
    def optimize_image(self, image_bytes: bytes, max_size_kb: int = 500) -> bytes:
        """Optimize image size while maintaining quality"""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Start with high quality
            quality = 90
            output = io.BytesIO()
            
            # Reduce quality until size is acceptable
            while quality > 20:
                output.seek(0)
                output.truncate()
                img.save(output, format='JPEG', quality=quality, optimize=True)
                
                if output.tell() <= max_size_kb * 1024:
                    break
                
                quality -= 10
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            logger.warning(f"Error optimizing image: {e}. Returning original.")
            return image_bytes
    
    def generate_image_filename(self, image_url: str, product_sku: str) -> str:
        """Generate a unique filename for the image"""
        # Extract extension from URL
        parsed_url = urlparse(image_url)
        path = parsed_url.path
        _, ext = os.path.splitext(path)
        
        # Default to .jpg if no extension found
        if not ext or ext not in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
            ext = '.jpg'
        
        # Create filename: SKU_hash
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
        filename = f"{product_sku}_{url_hash}{ext}"
        
        return filename
    
    def upload_to_s3(self, file_bytes: bytes, s3_key: str, content_type: str = 'image/jpeg') -> bool:
        """Upload file to S3"""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_bytes,
                ContentType=content_type,
                CacheControl='max-age=31536000'  # Cache for 1 year
            )
            logger.debug(f"Uploaded to S3: {s3_key}")
            return True
        except Exception as e:
            logger.error(f"Error uploading to S3 {s3_key}: {e}")
            return False
    
    def get_s3_url(self, s3_key: str) -> str:
        """Generate S3 URL for uploaded file"""
        return f"https://{self.bucket_name}.s3.{config.AWS_REGION}.amazonaws.com/{s3_key}"
    
    def download_and_upload_image(self, image_url: str, product_sku: str, s3_path: str) -> Dict:
        """
        Download image and upload to S3
        
        Returns:
            Dict with 'success', 's3_key', 's3_url', 'original_url'
        """
        result = {
            'success': False,
            's3_key': None,
            's3_url': None,
            'original_url': image_url
        }
        
        if not image_url:
            return result
        
        try:
            # Download image
            image_bytes = self.download_image(image_url)
            if not image_bytes:
                return result
            
            # Optimize image
            optimized_bytes = self.optimize_image(image_bytes)
            
            # Generate filename and S3 key
            filename = self.generate_image_filename(image_url, product_sku)
            s3_key = f"{s3_path}/{filename}"
            
            # Upload to S3
            if self.upload_to_s3(optimized_bytes, s3_key):
                result['success'] = True
                result['s3_key'] = s3_key
                result['s3_url'] = self.get_s3_url(s3_key)
            
        except Exception as e:
            logger.error(f"Error processing image {image_url}: {e}")
        
        return result
    
    def process_products_images(self, products: List[Dict], s3_path: str) -> List[Dict]:
        """
        Process all images for a list of products
        
        Args:
            products: List of product dicts
            s3_path: S3 path prefix for images
            
        Returns:
            List of products with updated image URLs
        """
        processed_urls: Set[str] = set()
        
        for product in tqdm(products, desc="Downloading images"):
            product_sku = product.get('sku', 'unknown')
            
            # Process main image
            main_image_url = product.get('image_url')
            if main_image_url and main_image_url not in processed_urls:
                result = self.download_and_upload_image(main_image_url, product_sku, s3_path)
                if result['success']:
                    product['s3_image_url'] = result['s3_url']
                    product['s3_image_key'] = result['s3_key']
                    processed_urls.add(main_image_url)
            
            # Process related product images
            related_products = product.get('related_products', [])
            if isinstance(related_products, list):
                for related in related_products:
                    if isinstance(related, dict):
                        related_image_url = related.get('thumbnail')
                        if related_image_url and related_image_url not in processed_urls:
                            related_sku = related.get('slug', product_sku)
                            result = self.download_and_upload_image(related_image_url, related_sku, s3_path)
                            if result['success']:
                                related['s3_thumbnail'] = result['s3_url']
                                processed_urls.add(related_image_url)
        
        return products
    
    def upload_excel_to_s3(self, excel_bytes: bytes, s3_key: str) -> bool:
        """Upload Excel file to S3"""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=excel_bytes,
                ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                CacheControl='max-age=3600'
            )
            logger.info(f"Uploaded Excel to S3: {s3_key}")
            return True
        except Exception as e:
            logger.error(f"Error uploading Excel to S3 {s3_key}: {e}")
            return False
    
    def batch_upload_excel_files(self, excel_files: Dict[str, bytes], s3_path_prefix: str) -> Dict[str, str]:
        """
        Upload multiple Excel files to S3
        
        Args:
            excel_files: Dict mapping filenames to file bytes
            s3_path_prefix: S3 path prefix (e.g., 'boutiqaat-data/year=2026/.../celebrities/excel_files')
            
        Returns:
            Dict mapping filenames to S3 URLs
        """
        uploaded_files = {}
        
        for filename, file_bytes in tqdm(excel_files.items(), desc="Uploading Excel files"):
            s3_key = f"{s3_path_prefix}/{filename}"
            if self.upload_excel_to_s3(file_bytes, s3_key):
                s3_url = self.get_s3_url(s3_key)
                uploaded_files[filename] = s3_url
        
        return uploaded_files


if __name__ == '__main__':
    # Test the image downloader
    downloader = ImageDownloader()
    
    # Test single image download
    test_url = "https://v2cdn.boutiqaat.com/cdn-cgi/image/width=466,height=466,quality=80/media/catalog/product//M/U/MU-00011099-1.jpg"
    result = downloader.download_and_upload_image(
        test_url,
        "TEST-SKU-001",
        "boutiqaat-data/test/images"
    )
    
    print(f"Upload result: {result}")
