"""
Configuration for categories, brands, and celebrities to scrape
Edit this file to customize what you want to scrape
"""

# CATEGORIES TO SCRAPE
# Format: {'name': 'Display Name', 'slug': 'url-path', 'category_url': 'full-url'}
# 
# Option 1: Provide category_url (recommended - most accurate):
#   {'name': 'Serums', 'category_url': 'https://www.boutiqaat.com/kw-ar/women/skin-care/face-serums-treatments/l/'}
#
# Option 2: Provide slug (fallback):
#   {'name': 'Serums', 'slug': 'skin-care/face-serums-treatments/l'}
#
# Option 3: Use discover_and_scrape_categories() to auto-discover all categories from a base page
#   Example: scraper.discover_and_scrape_categories('skin-care/c/') will find all skincare categories

CATEGORIES = [
    # Makeup Categories - Update with actual category_url from website
    {'name': 'Foundations', 'slug': 'makeup/foundations/l'},
    {'name': 'Lipsticks', 'slug': 'makeup/lipstick/l'},
    {'name': 'Lip Gloss', 'slug': 'makeup/lip-gloss/l'},
    {'name': 'Mascara', 'slug': 'makeup/mascara/l'},
    {'name': 'Blush', 'slug': 'makeup/blush/l'},
    {'name': 'Bronzer', 'slug': 'makeup/bronzer/l'},
    {'name': 'Eyeshadow', 'slug': 'makeup/eye-shadow/l'},
    {'name': 'Eyeliner', 'slug': 'makeup/eye-liner/l'},
    {'name': 'Concealer', 'slug': 'makeup/concealer/l'},
    {'name': 'Makeup Brushes', 'slug': 'makeup/makeup-brushes/l'},
    
    # Skincare Categories - Example with category_url
    # {'name': 'Face Serums & Treatments', 'category_url': 'https://www.boutiqaat.com/kw-ar/women/skin-care/face-serums-treatments/l/'},
    {'name': 'Moisturizers', 'slug': 'skin-care/moisturizers/l'},
    {'name': 'Cleansers', 'slug': 'skin-care/cleansers/l'},
    {'name': 'Serums', 'slug': 'skin-care/serum/l'},
    {'name': 'Sunscreen', 'slug': 'skin-care/sunscreen/l'},
    {'name': 'Face Masks', 'slug': 'skin-care/face-mask/l'},
    
    # Fragrance Categories
    {'name': 'Perfumes', 'slug': 'fragrances/perfumes-1/l'},
    {'name': 'Body Mists', 'slug': 'fragrances/body-mists/l'},
    
    # Hair Care
    {'name': 'Shampoo', 'slug': 'hair-care/shampoo/l'},
    {'name': 'Conditioner', 'slug': 'hair-care/conditioner/l'},
    {'name': 'Hair Styling', 'slug': 'hair-care/hair-styling/l'},
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
