"""
Boutiqaat Scraper using Scrapling library
Extracts products from categories, brands, and celebrities
"""
import json
import re
import time
from datetime import datetime
from typing import List, Dict, Optional
from scrapling import Fetcher
from tqdm import tqdm
import config
import logging

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


class BoutiqaatScraper:
    """Scraper for Boutiqaat products using Scrapling"""
    
    def __init__(self):
        """Initialize the scraper"""
        self.fetcher = Fetcher(auto_match=config.SCRAPLING_AUTO_MATCH)
        self.base_url = config.BASE_URL_AR_KW
        
    def extract_next_data(self, html_content: str) -> Optional[Dict]:
        """Extract __NEXT_DATA__ JSON from HTML"""
        try:
            # Find the script tag with __NEXT_DATA__
            pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
            match = re.search(pattern, html_content, re.DOTALL)
            
            if match:
                json_str = match.group(1).strip()
                data = json.loads(json_str)
                return data
            else:
                logger.warning("__NEXT_DATA__ script tag not found")
                return None
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error extracting NEXT_DATA: {e}")
            return None
    
    def fetch_page(self, url: str, max_retries: int = None) -> Optional[str]:
        """Fetch a page using Scrapling with retries"""
        max_retries = max_retries or config.MAX_RETRIES
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching: {url} (Attempt {attempt + 1}/{max_retries})")
                
                # Use Scrapling Fetcher to fetch the page
                page = self.fetcher.get(url, headers=config.HEADERS)
                
                if page and hasattr(page, 'body'):
                    return page.body
                elif page and hasattr(page, 'text'):
                    return page.text
                else:
                    logger.warning(f"Unexpected response type: {type(page)}")
                    
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(config.RETRY_DELAY * (attempt + 1))
                else:
                    logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                    
        return None
    
    def parse_products(self, next_data: Dict) -> List[Dict]:
        """Parse products from __NEXT_DATA__ structure"""
        try:
            products = []
            
            # Navigate the JSON structure
            page_props = next_data.get('props', {}).get('pageProps', {})
            response = page_props.get('response', {})
            products_data = response.get('products', [])
            
            # Products are nested in arrays - flatten them
            for product_array in products_data:
                if isinstance(product_array, list):
                    for product in product_array:
                        if isinstance(product, dict):
                            # Add scraped timestamp
                            product['scraped_at'] = datetime.now().isoformat()
                            
                            # Count related products
                            related = product.get('related_products', [])
                            product['related_products_count'] = len(related) if related else 0
                            
                            # Convert category_tree to string for Excel
                            if 'category_tree' in product:
                                product['category_tree'] = ' > '.join(
                                    [cat.get('category', '') for cat in product['category_tree']]
                                )
                            
                            # Convert gender array to string
                            if 'gender' in product and isinstance(product['gender'], list):
                                product['gender'] = ', '.join(product['gender'])
                            
                            products.append(product)
            
            logger.info(f"Parsed {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Error parsing products: {e}")
            return []
    
    def scrape_category(self, category_slug: str) -> List[Dict]:
        """Scrape products from a category"""
        url = f"{self.base_url}/{category_slug}"
        logger.info(f"Scraping category: {category_slug}")
        
        html = self.fetch_page(url)
        if not html:
            return []
        
        next_data = self.extract_next_data(html)
        if not next_data:
            return []
        
        return self.parse_products(next_data)
    
    def scrape_brand(self, brand_slug: str) -> List[Dict]:
        """Scrape products from a brand"""
        url = f"{self.base_url}/{brand_slug}/br/"
        logger.info(f"Scraping brand: {brand_slug}")
        
        html = self.fetch_page(url)
        if not html:
            return []
        
        next_data = self.extract_next_data(html)
        if not next_data:
            return []
        
        return self.parse_products(next_data)
    
    def scrape_celebrity(self, celebrity_slug: str) -> List[Dict]:
        """Scrape products from a celebrity"""
        url = f"{self.base_url}/{celebrity_slug}/cb/"
        logger.info(f"Scraping celebrity: {celebrity_slug}")
        
        html = self.fetch_page(url)
        if not html:
            return []
        
        next_data = self.extract_next_data(html)
        if not next_data:
            return []
        
        return self.parse_products(next_data)
    
    def scrape_categories(self, categories: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Scrape multiple categories
        
        Args:
            categories: List of dicts with 'name' and 'slug' keys
            
        Returns:
            Dict mapping category names to product lists
        """
        results = {}
        
        for category in tqdm(categories, desc="Scraping categories"):
            category_name = category.get('name', category.get('slug', 'unknown'))
            category_slug = category['slug']
            
            products = self.scrape_category(category_slug)
            results[category_name] = products
            
            time.sleep(1)  # Be respectful to the server
        
        return results
    
    def scrape_brands(self, brands: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Scrape multiple brands
        
        Args:
            brands: List of dicts with 'name' and 'slug' keys
            
        Returns:
            Dict mapping brand names to product lists
        """
        results = {}
        
        for brand in tqdm(brands, desc="Scraping brands"):
            brand_name = brand.get('name', brand.get('slug', 'unknown'))
            brand_slug = brand['slug']
            
            products = self.scrape_brand(brand_slug)
            results[brand_name] = products
            
            time.sleep(1)  # Be respectful to the server
        
        return results
    
    def scrape_celebrities(self, celebrities: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Scrape multiple celebrities
        
        Args:
            celebrities: List of dicts with 'name' and 'slug' keys
            
        Returns:
            Dict mapping celebrity names to product lists
        """
        results = {}
        
        for celebrity in tqdm(celebrities, desc="Scraping celebrities"):
            celebrity_name = celebrity.get('name', celebrity.get('slug', 'unknown'))
            celebrity_slug = celebrity['slug']
            
            products = self.scrape_celebrity(celebrity_slug)
            results[celebrity_name] = products
            
            time.sleep(1)  # Be respectful to the server
        
        return results


# Example usage and helper functions
def get_sample_categories():
    """Sample categories to scrape"""
    return [
        {'name': 'Foundations', 'slug': 'makeup/foundations/l'},
        {'name': 'Lipsticks', 'slug': 'makeup/lipstick/l'},
        {'name': 'Mascara', 'slug': 'makeup/mascara/l'},
        {'name': 'Perfumes', 'slug': 'fragrances/perfumes-1/l'},
    ]


def get_sample_brands():
    """Sample brands to scrape"""
    return [
        {'name': '114 Amatoury', 'slug': '114-amatoury'},
        {'name': 'MAC', 'slug': 'mac'},
        {'name': 'NARS', 'slug': 'nars'},
    ]


def get_sample_celebrities():
    """Sample celebrities to scrape"""
    return [
        {'name': 'Sana Mahdi Ansari', 'slug': 'sana-mahdi-ansari-1'},
        {'name': 'Kylie Jenner', 'slug': 'kylie-jenner'},
    ]


if __name__ == '__main__':
    # Test the scraper
    scraper = BoutiqaatScraper()
    
    # Test category scraping
    products = scraper.scrape_category('makeup/foundations/l')
    print(f"Found {len(products)} products in foundations category")
    
    if products:
        print("\nFirst product:")
        print(json.dumps(products[0], indent=2, ensure_ascii=False))
