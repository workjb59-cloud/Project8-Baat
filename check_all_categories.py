"""Check how many top-level categories are in shoplanding_category"""
from scraper import BoutiqaatScraper
import json

scraper = BoutiqaatScraper()

# Fetch any page (they all have the same navigation data)
html = scraper.fetch_page(f"{scraper.base_url}/makeup/c/")

if html:
    next_data = scraper.extract_next_data(html)
    
    if next_data:
        page_props = next_data.get('props', {}).get('pageProps', {})
        i_am_from_server = page_props.get('I_AM_FROM_SERVER', {})
        data_assets = i_am_from_server.get('dataAssets', {})
        categories_data = data_assets.get('categories', {})
        shoplanding = categories_data.get('shoplanding_category', [])
        
        print(f"Total top-level categories in shoplanding_category: {len(shoplanding)}")
        print("\n" + "="*80)
        print("TOP-LEVEL CATEGORIES:")
        print("="*80)
        
        for i, cat in enumerate(shoplanding, 1):
            name = cat.get('name', 'N/A')
            cat_id = cat.get('category_id', 'N/A')
            slug = cat.get('slug', 'N/A')
            children_count = len(cat.get('children', []))
            
            print(f"{i}. {name}")
            print(f"   ID: {cat_id}, Slug: {slug}")
            print(f"   Direct children: {children_count}")
            
            # Count total descendants
            def count_all(c):
                count = 1
                for child in c.get('children', []):
                    count += count_all(child)
                return count
            
            total = count_all(cat) - 1  # -1 to exclude self
            print(f"   Total descendants: {total}")
            print()
        
        print("="*80)
        print(f"So we have {len(shoplanding)} main categories available!")
        print("Not just the 4 we configured (makeup, skincare, fragrances, hair)")
