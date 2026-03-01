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
        # Initialize Fetcher with configuration
        self.fetcher = Fetcher(auto_match=config.SCRAPLING_AUTO_MATCH, storage="memory")
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
    
    def extract_categories_from_data(self, next_data: Dict) -> List[Dict]:
        """
        Extract category structure with URLs from __NEXT_DATA__
        
        Path: props.pageProps.I_AM_FROM_SERVER.dataAssets.categories.shoplanding_category
        """
        try:
            categories = []
            page_props = next_data.get('props', {}).get('pageProps', {})
            
            # Navigate to the correct path
            i_am_from_server = page_props.get('I_AM_FROM_SERVER', {})
            data_assets = i_am_from_server.get('dataAssets')
            
            if not data_assets:
                logger.warning("No dataAssets found in I_AM_FROM_SERVER")
                return categories
            
            # dataAssets can be null or contain categories
            categories_data = data_assets.get('categories', {}) if isinstance(data_assets, dict) else {}
            shoplanding_category = categories_data.get('shoplanding_category', [])
            
            if not shoplanding_category:
                logger.warning("No shoplanding_category found in dataAssets.categories")
                return categories
            
            def parse_category(cat_obj):
                """Recursively parse category and its children"""
                result = []
                if not cat_obj:
                    return result
                
                # Only include categories with URLs
                category_url = cat_obj.get('category_url')
                if category_url and cat_obj.get('active') == '1':
                    result.append({
                        'name': cat_obj.get('name', ''),
                        'category_url': category_url,
                        'category_id': cat_obj.get('category_id', ''),
                        'level': cat_obj.get('level', ''),
                        'slug': cat_obj.get('slug', ''),
                        'parent_id': cat_obj.get('parent_id', '')
                    })
                
                # Recursively parse children
                children = cat_obj.get('children', [])
                for child in children:
                    result.extend(parse_category(child))
                
                return result
            
            # Parse the category tree
            for cat in shoplanding_category:
                categories.extend(parse_category(cat))
            
            logger.info(f"Extracted {len(categories)} categories from __NEXT_DATA__")
            return categories
            
        except Exception as e:
            logger.error(f"Error extracting categories from __NEXT_DATA__: {e}")
            return []
    
    def extract_categories_from_html(self, html: str, base_slug: str) -> List[Dict]:
        """
        Extract category links from HTML
        
        Args:
            html: HTML content of the page
            base_slug: Base category slug (e.g., 'makeup/c/')
            
        Returns:
            List of category dicts with name, category_url, etc.
        """
        try:
            from bs4 import BeautifulSoup
            
            categories = []
            soup = BeautifulSoup(html, 'lxml')
            
            # Get the base category name from slug (e.g., 'makeup/c/' -> 'makeup')
            base_name = base_slug.replace('/c/', '').replace('/', '')
            
            # Find all links - look for subcategory links with /l/ (those contain products)
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Look for subcategory URLs with /l/ that match our base category
                # Example: /en-sa/women/makeup/foundations/l/
                if '/l/' in href and base_name in href.lower() and text:
                    # Extract the category path from the href
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        # href is like /en-kw/women/makeup/foundations/l/
                        # Extract the part after /women/ to reconstruct correct URL
                        if '/women/' in href:
                            path_after_women = href.split('/women/')[-1]
                            category_url = f"{self.base_url}/{path_after_women}"
                        else:
                            category_url = f"{self.base_url}{href}"
                    else:
                        category_url = href
                    
                    # Extract category ID if present (some URLs have /l/ID/ format)
                    category_id = ''
                    if '/l/' in href:
                        parts = href.split('/l/')
                        if len(parts) > 1 and parts[1].strip('/'):
                            category_id = parts[1].strip('/')
                    
                    # Only add unique categories
                    if category_url not in [cat['category_url'] for cat in categories]:
                        categories.append({
                            'name': text,
                            'category_url': category_url,
                            'category_id': category_id,
                            'level': '2'  # These are subcategories
                        })
            
            logger.info(f"Extracted {len(categories)} subcategories from HTML for {base_slug}")
            return categories
            
        except Exception as e:
            logger.error(f"Error extracting categories from HTML: {e}")
            return []
    
    def fetch_page(self, url: str, max_retries: int = None) -> Optional[str]:
        """Fetch a page using Scrapling with retries"""
        max_retries = max_retries or config.MAX_RETRIES
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching: {url} (Attempt {attempt + 1}/{max_retries})")
                
                # Use Scrapling Fetcher to fetch the page
                page = self.fetcher.get(url, headers=config.HEADERS)
                
                if page and hasattr(page, 'body'):
                    body = page.body
                    # Decode if bytes
                    if isinstance(body, bytes):
                        return body.decode('utf-8')
                    return body
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
            
            if not page_props:
                logger.warning("No pageProps found in __NEXT_DATA__")
                logger.warning(f"Available keys in props: {list(next_data.get('props', {}).keys())}")
                return []
            
            response = page_props.get('response', {})
            
            if not response:
                logger.warning("No response found in pageProps")
                logger.warning(f"Available keys in pageProps: {list(page_props.keys())}")
                return []
            
            products_data = response.get('products', [])
            
            if not products_data:
                logger.warning("No products array found in response")
                logger.warning(f"Available keys in response: {list(response.keys())}")
                logger.warning(f"Response type: {type(response)}")
                return []
            
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
        """
        Legacy method - constructs URL from slug (not recommended)
        Use scrape_category_url() or provide category_url in config instead
        """
        url = f"{self.base_url}/{category_slug}"
        logger.warning(f"⚠️  Using slug-based URL construction (not recommended): {category_slug}")
        logger.warning(f"   Consider using 'category_url' in your config instead")
        return self.scrape_category_url(url)

    def scrape_category_url(self, url: str) -> List[Dict]:
        """Scrape products from a category using the full category_url"""
        logger.info(f"Scraping category by URL: {url}")
        html = self.fetch_page(url)
        if not html:
            logger.error(f"Failed to fetch HTML for category URL: {url}")
            return []
        next_data = self.extract_next_data(html)
        if not next_data:
            logger.error(f"Failed to extract __NEXT_DATA__ for category URL: {url}")
            logger.warning(f"HTML length: {len(html)} characters")
            return []
        products = self.parse_products(next_data)
        logger.info(f"Successfully scraped {len(products)} products from {url}")
        return products
    
    def scrape_brand(self, brand_slug: str) -> List[Dict]:
        """Scrape products from a brand"""
        url = f"{self.base_url}/{brand_slug}/br/"
        logger.info(f"Scraping brand: {brand_slug}")
        logger.info(f"Full URL: {url}")
        
        html = self.fetch_page(url)
        if not html:
            logger.error(f"Failed to fetch HTML for brand: {brand_slug}")
            return []
        
        next_data = self.extract_next_data(html)
        if not next_data:
            logger.error(f"Failed to extract __NEXT_DATA__ for brand: {brand_slug}")
            logger.warning(f"HTML length: {len(html)} characters")
            return []
        
        products = self.parse_products(next_data)
        logger.info(f"Successfully scraped {len(products)} products from brand {brand_slug}")
        return products
    
    def scrape_celebrity(self, celebrity_slug: str) -> List[Dict]:
        """Scrape products from a celebrity"""
        url = f"{self.base_url}/{celebrity_slug}/cb/"
        logger.info(f"Scraping celebrity: {celebrity_slug}")
        logger.info(f"Full URL: {url}")
        
        html = self.fetch_page(url)
        if not html:
            logger.error(f"Failed to fetch HTML for celebrity: {celebrity_slug}")
            return []
        
        next_data = self.extract_next_data(html)
        if not next_data:
            logger.error(f"Failed to extract __NEXT_DATA__ for celebrity: {celebrity_slug}")
            logger.warning(f"HTML length: {len(html)} characters")
            return []
        
        products = self.parse_products(next_data)
        logger.info(f"Successfully scraped {len(products)} products from celebrity {celebrity_slug}")
        return products
    
    def discover_and_scrape_categories(self, base_category_slug: str) -> Dict[str, List[Dict]]:
        """
        Discover categories from a base category page and scrape all children
        
        Args:
            base_category_slug: Base category slug to discover from
                               - Specific slug like 'makeup/c/' or 'skin-care/c/'
                               - 'all' to discover ALL categories from entire site
            
        Returns:
            Dict mapping category names to product lists
        """
        results = {}
        
        # Fetch any page to get the full category tree (all pages have same navigation data)
        logger.info(f"Discovering categories from: {base_category_slug}")
        base_url = f"{self.base_url}/makeup/c/"  # Any page works, they all have full nav
        html = self.fetch_page(base_url)
        
        if not html:
            logger.error(f"Failed to fetch page for category discovery")
            return results
        
        # Extract __NEXT_DATA__ to get category tree
        next_data = self.extract_next_data(html)
        if not next_data:
            logger.error(f"Failed to extract __NEXT_DATA__")
            return results
        
        # Extract all categories from the JSON structure
        all_categories = self.extract_categories_from_data(next_data)
        
        if not all_categories:
            logger.warning(f"No categories discovered")
            return results
        
        # Filter categories based on base_category_slug
        if base_category_slug.lower() == 'all':
            # Discover ALL categories from the entire site
            discovered_categories = all_categories
            logger.info(f"Discovering ALL categories from entire site: {len(discovered_categories)} total")
        else:
            # Filter by slug prefix to get only categories under the specified base
            base_slug_clean = base_category_slug.replace('/c/', '').replace('/l/', '').strip('/')
            discovered_categories = [
                cat for cat in all_categories 
                if base_slug_clean in cat.get('slug', '').lower()
            ]
            logger.info(f"Discovered {len(discovered_categories)} categories under '{base_category_slug}'")
        
        if not discovered_categories:
            logger.warning(f"No categories match filter: {base_category_slug}")
            return results
        
        logger.info(f"Now scraping products from {len(discovered_categories)} categories...")
        
        # Scrape products from each discovered category
        for category in tqdm(discovered_categories, desc=f"Scraping {base_category_slug}"):
            category_name = category.get('name', 'unknown')
            category_url = category.get('category_url')
            
            if not category_url:
                logger.warning(f"No URL for category: {category_name}")
                continue
            
            products = self.scrape_category_url(category_url)
            results[category_name] = products
            
            time.sleep(1)  # Be respectful to the server
        
        return results
    
    def scrape_categories(self, categories: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Scrape multiple categories using category_url
        
        Args:
            categories: List of dicts with 'name' and 'category_url' keys
            
        Returns:
            Dict mapping category names to product lists
        """
        results = {}
        
        for category in tqdm(categories, desc="Scraping categories"):
            category_name = category.get('name', 'unknown')
            category_url = category.get('category_url')
            
            if not category_url:
                logger.error(f"❌ No category_url provided for '{category_name}', SKIPPING")
                logger.error(f"   Run 'python discover_categories.py' to get correct URLs")
                continue
            
            products = self.scrape_category_url(category_url)
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
