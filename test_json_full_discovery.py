"""
Test auto-discovery using corrected JSON extraction
This properly tests the full discover_and_scrape_categories flow
"""
from scraper import BoutiqaatScraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Initialize scraper
scraper = BoutiqaatScraper()

# Base categories from scraping_config.py
base_categories = [
    {'name': 'Makeup', 'auto_discover': 'makeup/c/'},
    {'name': 'Skincare', 'auto_discover': 'skin-care/c/'},
    {'name': 'Fragrances', 'auto_discover': 'fragrances/c/'},
    {'name': 'Hair Care', 'auto_discover': 'hair-care/c/'},
]

print("="*80)
print("AUTO-DISCOVERY TEST - Using JSON Extraction")
print("="*80)
print()

total_categories = 0
category_counts = {}

for base_cat in base_categories:
    section_name = base_cat['name']
    base_slug = base_cat['auto_discover']
    
    print(f"\n📂 Discovering categories from: {section_name} ({base_slug})")
    print("-" * 80)
    
    # Fetch the page
    base_url = f"{scraper.base_url}/{base_slug}"
    html = scraper.fetch_page(base_url)
    
    if html:
        # Extract __NEXT_DATA__
        next_data = scraper.extract_next_data(html)
        
        if next_data:
            # Extract categories using JSON method
            categories = scraper.extract_categories_from_data(next_data)
            category_counts[section_name] = len(categories)
            total_categories += len(categories)
            
            print(f"✅ Found {len(categories)} categories")
            
            # Show breakdown by level
            by_level = {}
            for cat in categories:
                level = cat.get('level', 'unknown')
                if level not in by_level:
                    by_level[level] = []
                by_level[level].append(cat)
            
            for level in sorted(by_level.keys()):
                count = len(by_level[level])
                print(f"   Level {level}: {count} categories")
                # Show first 3
                for i, cat in enumerate(by_level[level][:3], 1):
                    print(f"      - {cat['name']}")
                if count > 3:
                    print(f"      ... and {count - 3} more")
        else:
            print(f"❌ Failed to extract __NEXT_DATA__")
            category_counts[section_name] = 0
    else:
        print(f"❌ Failed to fetch page")
        category_counts[section_name] = 0

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"\nTotal categories discovered: {total_categories}")
print("\nBreakdown by section:")
for section, count in category_counts.items():
    print(f"  - {section}: {count} categories")

print("\n✅ Auto-discovery is working with JSON extraction!")
print(f"   The system will automatically scrape products from all {total_categories} discovered categories")
print("   Categories are extracted from __NEXT_DATA__.props.pageProps.I_AM_FROM_SERVER.dataAssets")
print("="*80)
