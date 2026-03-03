import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import time
from config import BASE_URL, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY

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

    def get_categories(self) -> List[Dict[str, str]]:
        """Scrape main makeup categories"""
        logger.info("Fetching categories...")
        soup = self._make_request(f'{self.base_url}/ar-kw/women/makeup/c/')
        
        if not soup:
            return []

        categories = []
        seen_urls = set()
        
        # Try multiple selector strategies
        selectors = [
            ('div', {'class': 'slick-slide'}),
            ('div', {'class_': lambda x: x and 'category' in x.lower()}),
            ('a', {'href': lambda x: x and '/makeup/' in x}),
        ]
        
        for tag, attrs in selectors:
            elements = soup.find_all(tag, attrs=attrs)
            logger.info(f"Trying selector {tag} with {attrs}: found {len(elements)}")
            
            if tag == 'div' and 'class' in attrs:
                # Handle slick-slide approach
                for elem in elements:
                    if 'slick-cloned' not in elem.get('class', []):
                        link = elem.find('a', href=True)
                        if link and '/makeup/' in link.get('href', ''):
                            href = link['href']
                            if href not in seen_urls:
                                seen_urls.add(href)
                                text_elem = elem.find('span', class_='font-width-dec')
                                if text_elem:
                                    category_name = text_elem.get_text(strip=True)
                                    full_url = urljoin(self.base_url, href)
                                    categories.append({
                                        'name': category_name,
                                        'url': full_url,
                                        'path': href
                                    })
            elif tag == 'a':
                # Handle direct link approach
                for link in elements:
                    href = link.get('href', '')
                    if href and '/makeup/' in href and href not in seen_urls:
                        seen_urls.add(href)
                        text = link.get_text(strip=True)
                        if text:
                            full_url = urljoin(self.base_url, href)
                            categories.append({
                                'name': text,
                                'url': full_url,
                                'path': href
                            })
            
            if categories:
                break
        
        logger.info(f"Found {len(categories)} categories")
        if categories:
            for cat in categories[:3]:
                logger.info(f"  - {cat['name']}")
        
        return categories

    def get_subcategories(self, category_url: str) -> List[Dict[str, str]]:
        """Scrape subcategories for a given category"""
        logger.info(f"Fetching subcategories from {category_url}")
        soup = self._make_request(category_url)
        
        if not soup:
            return []

        subcategories = []
        seen_urls = set()
        
        # Try multiple selector strategies
        slick_slides = soup.find_all('div', class_='slick-slide')
        
        for slide in slick_slides:
            if 'slick-cloned' not in slide.get('class', []):
                link = slide.find('a', href=True)
                if link and '/makeup/' in link.get('href', ''):
                    href = link['href']
                    if href not in seen_urls:
                        seen_urls.add(href)
                        text_elem = slide.find('span', class_='font-width-dec')
                        if text_elem:
                            sub_name = text_elem.get_text(strip=True)
                            full_url = urljoin(self.base_url, href)
                            subcategories.append({
                                'name': sub_name,
                                'url': full_url,
                                'path': href
                            })
        
        # Fallback: if no slick-slides found, try direct links
        if not subcategories:
            links = soup.find_all('a', href=lambda x: x and '/p/' in x)
            for link in links[:10]:
                href = link.get('href', '')
                if href not in seen_urls:
                    text = link.get_text(strip=True)
                    if text and len(text) > 0:
                        seen_urls.add(href)
                        full_url = urljoin(self.base_url, href)
                        subcategories.append({
                            'name': text,
                            'url': full_url,
                            'path': href
                        })
        
        logger.info(f"Found {len(subcategories)} subcategories")
        return subcategories
        
        logger.info(f"Found {len(subcategories)} subcategories")
        return subcategories

    def get_products(self, subcategory_url: str) -> List[Dict]:
        """Scrape all products in a subcategory with pagination"""
        logger.info(f"Fetching products from {subcategory_url}")
        all_products = []
        page = 1
        
        while True:
            page_url = f"{subcategory_url}?p={page}"
            soup = self._make_request(page_url)
            
            if not soup:
                break
            
            # Try multiple selectors
            products = soup.find_all('div', class_='single-product-wrap')
            if not products:
                products = soup.find_all('div', class_=lambda x: x and 'product' in x.lower())
            if not products:
                products = soup.find_all('article', class_=lambda x: x and 'product' in x.lower())
            
            if not products:
                logger.warning(f"No products found on page {page}")
                break
            
            logger.info(f"Found {len(products)} products on page {page}")
            
            for product in products:
                try:
                    product_data = self._extract_product_details(product)
                    if product_data:
                        all_products.append(product_data)
                except Exception as e:
                    logger.warning(f"Error extracting product details: {str(e)}")
                    continue
            
            # Check if there's a next page
            next_button = soup.find('a', rel='next')
            if not next_button:
                break
            
            page += 1
            time.sleep(1)  # Be respectful to the server
        
        logger.info(f"Found {len(all_products)} total products")
        return all_products

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
        soup = self._make_request(product_url)
        
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
