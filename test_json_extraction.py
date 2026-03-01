"""Test category extraction from __NEXT_DATA__ JSON (correct path)"""
from scraper import BoutiqaatScraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Initialize scraper
scraper = BoutiqaatScraper()

# Test URL
test_slug = 'makeup/c/'
base_url = f"{scraper.base_url}/{test_slug}"

print(f"Fetching: {base_url}")
print("="*80)

# Fetch the page
html = scraper.fetch_page(base_url)

if html:
    print(f"✅ Successfully fetched HTML ({len(html)} bytes)")
    
    # Extract __NEXT_DATA__
    next_data = scraper.extract_next_data(html)
    
    if next_data:
        print(f"✅ Successfully extracted __NEXT_DATA__")
        
        # Check the path structure
        page_props = next_data.get('props', {}).get('pageProps', {})
        i_am_from_server = page_props.get('I_AM_FROM_SERVER', {})
        data_assets = i_am_from_server.get('dataAssets')
        
        print(f"\nData structure check:")
        print(f"  - I_AM_FROM_SERVER exists: {bool(i_am_from_server)}")
        print(f"  - dataAssets type: {type(data_assets)}")
        
        if isinstance(data_assets, dict):
            categories_data = data_assets.get('categories', {})
            shoplanding = categories_data.get('shoplanding_category', [])
            print(f"  - categories exists: {bool(categories_data)}")
            print(f"  - shoplanding_category count: {len(shoplanding) if isinstance(shoplanding, list) else 0}")
        
        # Extract categories using the corrected method
        categories = scraper.extract_categories_from_data(next_data)
        
        print(f"\n✅ Extracted {len(categories)} categories from __NEXT_DATA__")
        print("\nCategories found:")
        print("="*80)
        
        # Group by level to show hierarchy
        by_level = {}
        for cat in categories:
            level = cat.get('level', 'unknown')
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(cat)
        
        for level in sorted(by_level.keys()):
            cats_at_level = by_level[level]
            print(f"\nLevel {level}: {len(cats_at_level)} categories")
            for i, cat in enumerate(cats_at_level[:5], 1):
                print(f"  {i}. {cat['name']} (ID: {cat['category_id']})")
            if len(cats_at_level) > 5:
                print(f"     ... and {len(cats_at_level) - 5} more")
        
        if len(categories) > 0:
            print(f"\n✅ SUCCESS: Category extraction from JSON is working!")
            print(f"   Total categories: {len(categories)}")
        else:
            print(f"\n❌ FAILED: No categories extracted from JSON")
    else:
        print("❌ Failed to extract __NEXT_DATA__")
else:
    print("❌ Failed to fetch page")
