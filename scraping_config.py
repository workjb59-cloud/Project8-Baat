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

CATEGORIES = [
    # Sample categories - Add more from discover_categories.py
    # Makeup
    {'name': 'Foundations', 'category_url': 'https://www.boutiqaat.com/kw-ar/women/makeup/foundations/l/'},
    {'name': 'Lipsticks', 'category_url': 'https://www.boutiqaat.com/kw-ar/women/makeup/lipstick/l/'},
    {'name': 'Mascara', 'category_url': 'https://www.boutiqaat.com/kw-ar/women/makeup/mascara/l/'},
    {'name': 'Eyeshadow', 'category_url': 'https://www.boutiqaat.com/kw-ar/women/makeup/eye-shadow/l/'},
    {'name': 'Brushes & Accessories', 'category_url': 'https://www.boutiqaat.com/kw-ar/women/makeup/brushes-accessories/l/'},
    
    # Skincare
    {'name': 'Face Serums & Treatments', 'category_url': 'https://www.boutiqaat.com/kw-ar/women/skin-care/face-serums-treatments/l/'},
    {'name': 'Moisturizers', 'category_url': 'https://www.boutiqaat.com/kw-ar/women/skin-care/moisturizers/l/'},
    {'name': 'Cleansers', 'category_url': 'https://www.boutiqaat.com/kw-ar/women/skin-care/cleansers/l/'},
    
    # Run 'python discover_categories.py' to get all categories with correct URLs
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
