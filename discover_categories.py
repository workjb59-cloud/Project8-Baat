"""
Example script to discover all categories from base category pages
This will fetch the category structure from the website and show all category_urls
"""
from scraper import BoutiqaatScraper
import json

def main():
    scraper = BoutiqaatScraper()
    
    # Base categories to discover from
    # Use the main category pages that contain subcategory lists
    base_categories = [
        'makeup/c/',        # All makeup categories
        'skin-care/c/',     # All skincare categories
        'fragrances/c/',    # All fragrance categories
        'hair-care/c/',     # All hair care categories
    ]
    
    all_discovered = {}
    
    for base_slug in base_categories:
        print(f"\n{'='*80}")
        print(f"Discovering categories from: {base_slug}")
        print(f"{'='*80}\n")
        
        # Fetch the base category page
        base_url = f"{scraper.base_url}/{base_slug}"
        html = scraper.fetch_page(base_url)
        
        if not html:
            print(f"❌ Failed to fetch {base_slug}")
            continue
        
        next_data = scraper.extract_next_data(html)
        if not next_data:
            print(f"❌ Failed to extract data from {base_slug}")
            continue
        
        # Extract categories
        categories = scraper.extract_categories_from_data(next_data)
        
        if not categories:
            print(f"⚠️  No categories found in {base_slug}")
            continue
        
        print(f"✅ Found {len(categories)} categories\n")
        
        # Store discovered categories
        all_discovered[base_slug] = categories
        
        # Display discovered categories
        for cat in categories:
            print(f"  📁 {cat['name']}")
            print(f"     URL: {cat['category_url']}")
            print(f"     ID: {cat['category_id']}, Level: {cat['level']}")
            print()
    
    # Save to JSON file for reference
    with open('discovered_categories.json', 'w', encoding='utf-8') as f:
        json.dump(all_discovered, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print(f"✅ Discovery complete! Saved to: discovered_categories.json")
    print(f"{'='*80}\n")
    
    # Show how to use in scraping_config.py
    print("💡 To use these URLs in scraping_config.py:\n")
    print("CATEGORIES = [")
    for base_slug, categories in all_discovered.items():
        for cat in categories[:3]:  # Show first 3 as examples
            print(f"    {{'name': '{cat['name']}', 'category_url': '{cat['category_url']}'}},")
    print("    # ... add more categories")
    print("]\n")

if __name__ == '__main__':
    main()
