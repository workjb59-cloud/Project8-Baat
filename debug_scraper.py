#!/usr/bin/env python
"""Debug script to inspect the website structure and find product selectors"""

import requests
from bs4 import BeautifulSoup
from config import BASE_URL, REQUEST_TIMEOUT

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

# Test category URL - products should be here
test_url = 'https://www.boutiqaat.com/ar-bh/women/makeup/foundations/l/'
print(f"Fetching: {test_url}\n")

try:
    response = session.get(test_url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print("=" * 80)
    print("PRODUCT PAGE DEBUG")
    print("=" * 80)
    
    # Check for single-product-wrap
    print("\n1. Looking for 'single-product-wrap' divs:")
    single_products = soup.find_all('div', class_='single-product-wrap')
    print(f"   Found: {len(single_products)}")
    
    # Check for product-like divs
    print("\n2. Looking for divs with 'product' in class:")
    product_divs = soup.find_all('div', class_=lambda x: x and 'product' in str(x).lower())
    print(f"   Found: {len(product_divs)}")
    if product_divs:
        for i, div in enumerate(product_divs[:3]):
            print(f"   Example {i+1}: class='{div.get('class')}'")
    
    # Check for articles
    print("\n3. Looking for article elements:")
    articles = soup.find_all('article')
    print(f"   Found: {len(articles)}")
    if articles:
        for i, article in enumerate(articles[:3]):
            print(f"   Example {i+1}: class='{article.get('class')}'")
    
    # Check for links
    print("\n4. Looking for product links (href with /p/):")
    product_links = soup.find_all('a', href=lambda x: x and '/p/' in x)
    print(f"   Found: {len(product_links)}")
    for i, link in enumerate(product_links[:5]):
        print(f"   - {link.get('href', 'NO HREF')}")
    
    # Check for images
    print("\n5. Looking for images:")
    images = soup.find_all('img')
    print(f"   Total images: {len(images)}")
    product_images = [img for img in images if img.get('data-src') or img.get('src')]
    print(f"   Images with src/data-src: {len(product_images)}")
    
    # Look for grid/list containers
    print("\n6. Looking for grid containers (ul, ol, div with grid/list class):")
    containers = soup.find_all(['ul', 'ol'], class_=lambda x: x and ('grid' in str(x).lower() or 'list' in str(x).lower()))
    print(f"   Found containers: {len(containers)}")
    
    # Check page structure
    print("\n7. Page structure:")
    main = soup.find('main') or soup.find('div', class_=lambda x: x and 'main' in str(x).lower())
    if main:
        print(f"   Main element found: {main.name}")
        children = main.find_all(['div', 'section', 'article'], recursive=False)
        print(f"   Direct children: {len(children)}")
    
    # Look for any container with multiple links (likely product list)
    print("\n8. Looking for containers with multiple product links:")
    all_divs = soup.find_all('div', class_=lambda x: x and x)
    for div in all_divs[:50]:
        links_in_div = len(div.find_all('a', href=True, recursive=False))
        if links_in_div >= 3:
            print(f"   Div with {links_in_div} direct links: class='{div.get('class')}'")
            break
    
    # Save HTML for inspection
    print("\n9. Saving HTML for inspection...")
    with open('debug_page.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("   Saved to debug_page.html")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()

