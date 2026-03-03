import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import time
from config import BASE_URL, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY

try:
    from scrapling import Scraper as ScraplingClient
    HAS_SCRAPLING = True
except ImportError:
    HAS_SCRAPLING = False
    ScraplingClient = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BoutiqaatScraper:
    """Web scraper for Boutiqaat makeup products"""

    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.scrapling_client = None
        self.has_scrapling = False
        
        if HAS_SCRAPLING:
            try:
                self.scrapling_client = ScraplingClient()
                self.has_scrapling = True
                logger.info("Scrapling initialized for JavaScript-heavy pages")
            except Exception as e:
                logger.warning(f"Failed to initialize Scrapling: {str(e)}")
                self.has_scrapling = False

    def _make_request(self, url: str, retries: int = MAX_RETRIES) -> Optional[BeautifulSoup]:
        """Make HTTP request with retry logic"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1}/{retries} failed for {url}: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None

    def _make_request_with_js(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch page with JavaScript rendering using Scrapling"""
        if not self.has_scrapling or not self.scrapling_client:
            logger.warning("Scrapling not available, falling back to requests")
            return self._make_request(url)
        
        try:
            logger.info(f"Fetching with Scrapling (JS rendering): {url}")
            html = self.scrapling_client.scrape(url)
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logger.warning(f"Scrapling failed for {url}: {str(e)}")
            # Fallback to regular requests
            return self._make_request(url)

    def get_categories(self) -> List[Dict[str, str]]:
        """Scrape main makeup categories from the main category page"""
        logger.info("Fetching categories from /ar-kw/women/makeup/c/...")
        soup = self._make_request(f'{self.base_url}/ar-kw/women/makeup/c/')
        
        if not soup:
            return []

        categories = []
        seen_urls = set()
        
        # Look for all links in the main category page
        # Categories follow pattern: /ar-kw/women/makeup/{category-name}/l/
        all_links = soup.find_all('a', href=True)
        logger.info(f"Found {len(all_links)} total links on page")
        
        # Debug: Check a few links to see patterns
        debug_count = 0
        for link in all_links[:20]:
            href = link.get('href', '')
            if debug_count < 5:
                logger.debug(f"Link {debug_count}: {href}")
                debug_count += 1
        
        for link in all_links:
            href = link.get('href', '')
            
            # Match pattern: /makeup/{category}/l/ but not /makeup/c/
            if href and '/makeup/' in href and '/l/' in href and '/makeup/c' not in href:
                # Additional check: must end with /l/ or /l/?...
                if href.endswith('/l/') or '/l/' in href and (href.split('/l/')[1] == '' or href.split('/l/')[1].startswith('?')):
                    if href not in seen_urls:
                        seen_urls.add(href)
                        
                        # Extract category name from path
                        # e.g., /ar-kw/women/makeup/face/l/ -> face
                        path_parts = href.strip('/').split('/')
                        if len(path_parts) >= 2:
                            # The part before /l/ is the category name
                            category_name = path_parts[-2]
                            
                            # Get display text from link
                            text = link.get_text(strip=True)
                            
                            if category_name and len(category_name) > 1:
                                full_url = urljoin(self.base_url, href)
                                categories.append({
                                    'name': text if text and len(text) > 0 else category_name,
                                    'url': full_url,
                                    'path': href
                                })
        
        logger.info(f"Found {len(categories)} main categories")
        if categories:
            for cat in categories[:5]:
                logger.info(f"  - {cat['name']}: {cat['url']}")
        
        return categories

    def get_subcategories(self, category_url: str) -> List[Dict[str, str]]:
        """Scrape subcategories from a main category page"""
        logger.info(f"Fetching subcategories from {category_url}")
        soup = self._make_request(category_url)
        
        if not soup:
            return []

        subcategories = []
        seen_urls = set()
        
        # Extract main category name from URL (before calling this)
        path_parts = category_url.strip('/').split('/')
        main_category = path_parts[-2] if len(path_parts) >= 2 else 'unknown'
        
        # Look for all links with pattern /makeup/{subcategory}/l/
        # excluding the main category page itself
        all_links = soup.find_all('a', href=True)
        logger.info(f"Scanning {len(all_links)} links for subcategories")
        
        for link in all_links:
            href = link.get('href', '')
            
            # Match pattern: /makeup/{subcategory}/l/ 
            # but exclude /makeup/c/ and the main category page itself
            if (href and '/makeup/' in href and '/l/' in href and 
                '/makeup/c' not in href and href not in seen_urls):
                
                # Extract the subcategory name
                path_parts = href.strip('/').split('/')
                if len(path_parts) >= 2:
                    subcategory_name = path_parts[-2]
                    
                    # Skip if it's the main category page itself
                    if subcategory_name != main_category:
                        seen_urls.add(href)
                        text = link.get_text(strip=True)
                        
                        if subcategory_name and len(subcategory_name) > 1:
                            full_url = urljoin(self.base_url, href)
                            subcategories.append({
                                'name': text if text and len(text) > 0 else subcategory_name,
                                'url': full_url,
                                'path': href
                            })
        
        logger.info(f"Found {len(subcategories)} subcategories")
        if subcategories:
            for sub in subcategories[:5]:
                logger.info(f"  - {sub['name']}: {sub['url']}")
        
        return subcategories

    def get_products(self, category_url: str) -> List[Dict]:
        """Scrape products from a category page, organized by subcategory"""
        logger.info(f"Fetching products from {category_url}")
        all_products = []
        page = 1
        
        while True:
            # Build pagination URL
            page_url = f"{category_url}?p={page}" if '?' not in category_url else f"{category_url}&p={page}"
            logger.info(f"Fetching page {page}: {page_url}")
            
            # Use Scrapling for JS-heavy product pages
            soup = self._make_request_with_js(page_url)
            
            if not soup:
                break
            
            # Extract products - will try to identify subcategories
            page_products = self._extract_products_with_subcategories(soup)
            
            if page_products:
                logger.info(f"Found {len(page_products)} products on page {page}")
                all_products.extend(page_products)
            else:
                logger.warning(f"No products found on page {page}")
                break
            
            # Check if there's a next page
            next_button = soup.find('a', rel='next')
            if not next_button:
                logger.info("No next page found")
                break
            
            page += 1
            time.sleep(1)  # Be respectful to the server
        
        logger.info(f"Found {len(all_products)} total products")
        return all_products
    
    def _extract_products_with_subcategories(self, soup) -> List[Dict]:
        """Extract products from page while trying to identify subcategories"""
        # First try to find products organized by subcategory sections
        products = self._extract_by_sections(soup)
        if products:
            logger.info(f"Extracted {len(products)} products with subcategories")
            return products
        
        # Fallback: extract all products without subcategory grouping
        products = self._extract_all_products(soup)
        if products:
            logger.info(f"Extracted {len(products)} products (no subcategories found)")
        
        return products
    
    def _extract_by_sections(self, soup) -> List[Dict]:
        """Extract products organized by subcategory sections/headers"""
        products = []
        
        # Look for heading elements (h2, h3, h4) that indicate subcategories
        headings = soup.find_all(['h2', 'h3', 'h4'])
        
        for heading in headings:
            heading_text = heading.get_text(strip=True)
            if not heading_text or len(heading_text) < 2:
                continue
            
            # Find the next container with products
            container = heading.find_next(['div', 'section', 'ul', 'ol'])
            if not container:
                continue
            
            # Extract products from this container
            section_products = self._find_products_in_container(container)
            
            if section_products:
                logger.info(f"Section '{heading_text}': {len(section_products)} products")
                
                # Add subcategory info to each product
                for product_data in section_products:
                    if product_data:
                        product_data['subcategory'] = heading_text
                        products.append(product_data)
        
        return products
    
    def _extract_all_products(self, soup) -> List[Dict]:
        """Extract all products from a page without subcategory grouping"""
        products = []
        product_elements = []
        
        # Strategy 1: div.single-product-wrap
        product_elements = soup.find_all('div', class_='single-product-wrap')
        if product_elements:
            logger.debug(f"Strategy 1 (single-product-wrap): found {len(product_elements)}")
        
        # Strategy 2: Any div with 'product' in class
        if not product_elements:
            product_elements = soup.find_all('div', class_=lambda x: x and 'product' in str(x).lower())
            if product_elements:
                logger.debug(f"Strategy 2 (div with product): found {len(product_elements)}")
        
        # Strategy 3: article elements
        if not product_elements:
            product_elements = soup.find_all('article')
            if product_elements:
                logger.debug(f"Strategy 3 (article): found {len(product_elements)}")
        
        # Strategy 4: Elements with links and images
        if not product_elements:
            all_elems = soup.find_all(['div', 'article', 'li'])
            product_elements = [e for e in all_elems if e.find('a', href=True) and e.find('img')]
            if product_elements:
                logger.debug(f"Strategy 4 (link+image): found {len(product_elements)}")
        
        for elem in product_elements:
            product_data = self._extract_product_details(elem)
            if product_data:
                products.append(product_data)
        
        return products
    
    def _find_products_in_container(self, container) -> List[Dict]:
        """Find and extract products from a container element"""
        products = []
        
        # Look for product elements within container
        product_elems = container.find_all('div', class_='single-product-wrap')
        
        if not product_elems:
            product_elems = container.find_all('div', class_=lambda x: x and 'product' in str(x).lower())
        
        if not product_elems:
            product_elems = container.find_all('article')
        
        if not product_elems:
            product_elems = container.find_all('li')
        
        for elem in product_elems:
            product_data = self._extract_product_details(elem)
            if product_data:
                products.append(product_data)
        
        return products

    def _extract_product_details(self, product_elem) -> Optional[Dict]:
        """Extract details from a single product element"""
        try:
            # Product name - try multiple selectors
            name_elem = product_elem.find('span', class_='product-name-plp-h3')
            if not name_elem:
                name_elem = product_elem.find('h2') or product_elem.find('h3')
            if not name_elem:
                name_elem = product_elem.find(class_=lambda x: x and 'name' in x.lower())
            name = name_elem.get_text(strip=True) if name_elem else 'Unknown'
            
            # Brand - try multiple selectors
            brand_elem = product_elem.find('span', class_='brand-name')
            if not brand_elem:
                brand_elem = product_elem.find(class_=lambda x: x and 'brand' in x.lower())
            brand = brand_elem.get_text(strip=True) if brand_elem else 'Unknown'
            
            # Price - try multiple selectors
            price_elem = product_elem.find('span', class_='new-price')
            if not price_elem:
                price_elem = product_elem.find(class_=lambda x: x and 'price' in x.lower())
            price = price_elem.get_text(strip=True) if price_elem else 'N/A'
            
            # Product URL - try multiple selectors
            link_elem = product_elem.find('a', {'class': 'product-image'})
            if not link_elem:
                link_elem = product_elem.find('a', href=True)
            product_url = urljoin(self.base_url, link_elem['href']) if link_elem and link_elem.get('href') else None
            
            # Image URL - try multiple selectors
            img_elem = product_elem.find('img', class_='img-fluid')
            if not img_elem:
                img_elem = product_elem.find('img')
            image_url = img_elem.get('src') or img_elem.get('data-src') if img_elem else None
            
            # Color options
            colors = 'N/A'
            all_spans = product_elem.find_all('span')
            for span in all_spans:
                text = span.get_text(strip=True)
                if 'ألوان' in text or 'لون' in text or 'colors' in text.lower():
                    colors = text
                    break
            
            if not product_url:
                return None
            
            return {
                'name': name,
                'brand': brand,
                'price': price,
                'url': product_url,
                'image_url': image_url,
                'colors': colors
            }
        except Exception as e:
            logger.warning(f"Error extracting product: {str(e)}")
            return None

    def get_product_full_details(self, product_url: str) -> Optional[Dict]:
        """Scrape full details from product page"""
        logger.info(f"Fetching full details from {product_url}")
        soup = self._make_request_with_js(product_url)
        
        if not soup:
            return None
        
        try:
            # Product name
            name_elem = soup.find('h1', class_='product-name-h1')
            name = name_elem.get_text(strip=True) if name_elem else 'Unknown'
            
            # Price
            price_elem = soup.find('span', class_='new-price')
            price = price_elem.get_text(strip=True) if price_elem else 'N/A'
            
            # Brand
            brand_elem = soup.find('a', class_='brand-title')
            brand = brand_elem.get_text(strip=True) if brand_elem else 'Unknown'
            
            # Description
            desc_elem = soup.find('div', class_='content-color')
            description = desc_elem.get_text(strip=True) if desc_elem else 'N/A'
            
            # Rating
            rating_elem = soup.find('span', class_='product-ratting')
            rating = 'N/A'
            if rating_elem:
                # Count filled stars
                filled_stars = len(rating_elem.find_all('span', style=lambda x: x and 'width: 100%' in x))
                rating = f"{filled_stars}/5"
            
            # Review count
            review_elem = soup.find('a', href=lambda x: x and 'review' in str(x).lower())
            reviews = 'N/A'
            if review_elem:
                reviews = review_elem.get_text(strip=True)
            
            # SKU
            sku_elem = soup.find('span', class_='attr-level-val')
            sku = sku_elem.get_text(strip=True) if sku_elem else 'N/A'
            
            # Product image (from details page)
            img_elem = soup.find('img', class_='img-fluid')
            main_image = img_elem.get('src') if img_elem else None
            
            return {
                'name': name,
                'brand': brand,
                'price': price,
                'description': description,
                'rating': rating,
                'reviews': reviews,
                'sku': sku,
                'image_url': main_image,
                'product_url': product_url
            }
        except Exception as e:
            logger.warning(f"Error extracting full details: {str(e)}")
            return None
