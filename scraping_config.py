"""
Configuration for categories, brands, and celebrities to scrape
Edit this file to customize what you want to scrape
"""

# IMPORTANT: Categories now REQUIRE 'category_url' (not slug)
# 
# HOW TO GET CATEGORY URLs:
# Run this command to discover all category URLs from the website:
#   python discover_categories.py
#
# This will create 'discovered_categories.json' with all correct URLs
# Then copy the URLs here

# CATEGORIES TO SCRAPE
# Format: {'name': 'Display Name', 'category_url': 'full-url'}

# CATEGORIES TO SCRAPE
# 
# Option 1: AUTO-DISCOVER ALL (Recommended - Discovers all 18+ main categories with 500+ subcategories)
# Format: {'name': 'All Categories', 'auto_discover': 'all'}
#
# Option 2: AUTO-DISCOVER SPECIFIC SECTION
# Provide base category slug to discover only that section
# Format: {'name': 'Section Name', 'auto_discover': 'base-category-slug'}
#
# Option 3: MANUAL
# Provide specific category URLs
# Format: {'name': 'Category Name', 'category_url': 'full-url'}

CATEGORIES = [
    # Option 1: Discover ALL categories from entire site (18 main categories, 509+ total)
    {'name': 'All Categories', 'auto_discover': 'all'},
    
    # Or Option 2: Auto-discover specific sections only:
    # {'name': 'Makeup', 'auto_discover': 'makeup/c/'},
    # {'name': 'Skincare', 'auto_discover': 'skin-care/c/'},
    # {'name': 'Korean Beauty', 'auto_discover': 'korean-beauty/c/'},
    # {'name': 'Arabic Fragrances', 'auto_discover': 'arabic-fragrances-1/c/'},
    # {'name': 'International Fragrances', 'auto_discover': 'fragrances-1/c/'},
    # {'name': 'Hair', 'auto_discover': 'hair/c/'},
    # {'name': 'Bath & Body', 'auto_discover': 'bath-body/c/'},
    # {'name': 'Eyewear', 'auto_discover': 'eyewear/c/'},
    # {'name': 'Contact Lenses', 'auto_discover': 'contact-lenses-3/c/'},
    # {'name': 'Apparel', 'auto_discover': 'apparel-1/c/'},
    # {'name': 'Footwear', 'auto_discover': 'footwear-1/c/'},
    # {'name': 'Sports', 'auto_discover': 'sports-1/c/'},
    # {'name': 'Derma Beauty', 'auto_discover': 'derma-beauty-women-level-1/c/'},
    # {'name': 'Electronics', 'auto_discover': 'electronics-1/c/'},
    # {'name': 'Home & Living', 'auto_discover': 'home-living-846333918/c/'},
    # {'name': 'Accessories', 'auto_discover': 'accessories-1/c/'},
    # {'name': 'Watches', 'auto_discover': 'watches-1/c/'},
    
    # Or Option 3: Add specific categories manually:
    # {'name': 'Foundations', 'category_url': 'https://www.boutiqaat.com/kw-ar/women/makeup/foundations/l/'},
]


# BRANDS TO SCRAPE
# Format: {'name': 'Brand Name', 'slug': 'brand-slug'}
# Find slugs from brand URLs like: https://www.boutiqaat.com/ar-kw/women/mac/br/
# The slug would be: 'mac'

BRANDS = [
    # International Beauty Brands
    {'name': '114 Amatoury', 'slug': '114-amatoury'},
    {'name': 'MAC', 'slug': 'mac'},
    {'name': 'NARS', 'slug': 'nars'},
    {'name': 'Charlotte Tilbury', 'slug': 'charlotte-tilbury'},
    {'name': 'Giorgio Armani', 'slug': 'giorgio-armani'},
    {'name': 'Make Up For Ever', 'slug': 'make-up-for-ever'},
    {'name': 'Kylie Cosmetics', 'slug': 'kylie-cosmetics'},
    {'name': 'Huda Beauty', 'slug': 'huda-beauty'},
    {'name': 'Fenty Beauty', 'slug': 'fenty-beauty'},
    {'name': 'Urban Decay', 'slug': 'urban-decay'},
    {'name': 'Too Faced', 'slug': 'too-faced'},
    {'name': 'Anastasia Beverly Hills', 'slug': 'anastasia-beverly-hills'},
    {'name': 'Bobbi Brown', 'slug': 'bobbi-brown'},
    {'name': 'Estee Lauder', 'slug': 'estee-lauder'},
    {'name': 'Clinique', 'slug': 'clinique'},
    {'name': 'Lancome', 'slug': 'lancome'},
    {'name': 'Dior', 'slug': 'dior'},
    {'name': 'YSL', 'slug': 'yves-saint-laurent'},
    {'name': 'La Mer', 'slug': 'la-mer'},
    {'name': 'SK-II', 'slug': 'sk-ii'},
    
    # Korean Beauty
    {'name': 'Innisfree', 'slug': 'innisfree'},
    {'name': 'Etude House', 'slug': 'etude-house'},
    {'name': 'Laneige', 'slug': 'laneige'},
    {'name': 'The Face Shop', 'slug': 'the-face-shop'},
    
    # Fragrances
    {'name': 'Tom Ford', 'slug': 'tom-ford'},
    {'name': 'Jo Malone', 'slug': 'jo-malone-london'},
    {'name': 'Creed', 'slug': 'creed'},
]


# CELEBRITIES TO SCRAPE
# Format: {'name': 'Celebrity Name', 'slug': 'celebrity-slug'}
# Find slugs from celebrity URLs like: https://www.boutiqaat.com/ar-kw/women/kylie-jenner/cb/
# The slug would be: 'kylie-jenner'

CELEBRITIES = [
    {'name': 'Kylie Jenner', 'slug': 'kylie-jenner'},
    {'name': 'Sana Mahdi Ansari', 'slug': 'sana-mahdi-ansari-1'},
    {'name': 'Huda Kattan', 'slug': 'huda-kattan'},
    {'name': 'Kim Kardashian', 'slug': 'kim-kardashian'},
    {'name': 'Rihanna', 'slug': 'rihanna'},
    # Add more celebrities as needed
]


# SCRAPING OPTIONS
# Set to False to skip scraping that data type
SCRAPE_CATEGORIES = True
SCRAPE_BRANDS = True
SCRAPE_CELEBRITIES = True

# DOWNLOAD OPTIONS
DOWNLOAD_IMAGES = True  # Set to False to skip image downloads
OPTIMIZE_IMAGES = True  # Set to False to keep original image sizes


def get_categories():
    """Get the list of categories to scrape"""
    if SCRAPE_CATEGORIES:
        return CATEGORIES
    return []


def get_brands():
    """Get the list of brands to scrape"""
    if SCRAPE_BRANDS:
        return BRANDS
    return []


def get_celebrities():
    """Get the list of celebrities to scrape"""
    if SCRAPE_CELEBRITIES:
        return CELEBRITIES
    return []


if __name__ == '__main__':
    # Print configuration summary
    print("=" * 80)
    print("SCRAPING CONFIGURATION")
    print("=" * 80)
    print(f"\nCategories to scrape: {len(get_categories())}")
    print(f"Brands to scrape: {len(get_brands())}")
    print(f"Celebrities to scrape: {len(get_celebrities())}")
    print(f"\nDownload images: {DOWNLOAD_IMAGES}")
    print(f"Optimize images: {OPTIMIZE_IMAGES}")
    print("\nTo modify what gets scraped, edit scraping_config.py")
    print("=" * 80)
