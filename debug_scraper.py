#!/usr/bin/env python
"""Debug script to inspect the website structure"""

import requests
from bs4 import BeautifulSoup
from config import BASE_URL, REQUEST_TIMEOUT

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

category_url = f'{BASE_URL}/ar-kw/women/makeup/c/'
print(f"Fetching: {category_url}\n")

try:
    response = session.get(category_url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print("=" * 80)
    print("HTML STRUCTURE DEBUG")
    print("=" * 80)
    
    # Check for slick-slide elements
    print("\n1. Looking for 'slick-slide' divs:")
    slick_slides = soup.find_all('div', class_='slick-slide')
    print(f"   Found: {len(slick_slides)} slides")
    if slick_slides:
        print(f"   First slide: {slick_slides[0][:200]}")
    
    # Check for product-like divs
    print("\n2. Looking for product containers (class containing 'product', 'item', 'category'):")
    for class_name in ['product', 'item', 'category', 'cat-item', 'makeup-category']:
        elements = soup.find_all(class_=lambda x: x and class_name in x.lower())
        print(f"   {class_name}: {len(elements)} found")
    
    # Check for all links with href containing makeup
    print("\n3. Looking for links with 'makeup' in href:")
    makeup_links = soup.find_all('a', href=lambda x: x and 'makeup' in x.lower())
    print(f"   Found: {len(makeup_links)} links")
    for i, link in enumerate(makeup_links[:5]):
        print(f"   - {link.get('href', 'NO HREF')}")
    
    # Check for category selections
    print("\n4. Looking for category navigation:")
    nav_elements = soup.find_all(['nav', 'ul', 'div'], class_=lambda x: x and 'cat' in str(x).lower())
    print(f"   Found {len(nav_elements)} navigation elements")
    
    # Display full page structure near beginning
    print("\n5. Page title and meta:")
    print(f"   Title: {soup.title.string if soup.title else 'NO TITLE'}")
    
    # Save HTML for manual inspection
    with open('debug_page.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify()[:5000])
    print("\n   Saved first 5000 chars to debug_page.html")
    
except Exception as e:
    print(f"Error: {str(e)}")
