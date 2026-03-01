# How to Setup Categories with Correct URLs

The scraper now **requires** `category_url` for each category (not slugs). This ensures you always scrape from the correct, canonical URLs.

## Quick Setup (3 Steps)

### Step 1: Discover Category URLs

Run the discovery script to fetch all category URLs from the website:

```bash
python discover_categories.py
```

This will:
- ✅ Fetch category structures from makeup, skincare, fragrances, and hair-care
- ✅ Extract all `category_url` values from the website
- ✅ Save them to `discovered_categories.json`
- ✅ Display formatted output for easy copy/paste

**Example Output:**
```
✅ Found 45 categories

  📁 Face Serums & Treatments
     URL: https://www.boutiqaat.com/kw-ar/women/skin-care/face-serums-treatments/l/
     ID: 1208, Level: 5

  📁 Foundations
     URL: https://www.boutiqaat.com/kw-ar/women/makeup/foundations/l/
     ID: 363, Level: 5
```

### Step 2: Copy URLs to Config

Open `scraping_config.py` and add the categories you want to scrape:

```python
CATEGORIES = [
    {'name': 'Face Serums & Treatments', 'category_url': 'https://www.boutiqaat.com/kw-ar/women/skin-care/face-serums-treatments/l/'},
    {'name': 'Foundations', 'category_url': 'https://www.boutiqaat.com/kw-ar/women/makeup/foundations/l/'},
    {'name': 'Lipsticks', 'category_url': 'https://www.boutiqaat.com/kw-ar/women/makeup/lipstick/l/'},
    # Add more categories...
]
```

### Step 3: Run the Scraper

```bash
python main.py
```

Or push to GitHub to trigger the workflow.

---

## Alternative: Use discover_and_scrape_categories()

If you want to scrape ALL categories from a section automatically:

```python
from scraper import BoutiqaatScraper

scraper = BoutiqaatScraper()

# Scrape all skincare categories
skincare_results = scraper.discover_and_scrape_categories('skin-care/c/')

# Scrape all makeup categories
makeup_results = scraper.discover_and_scrape_categories('makeup/c/')
```

This will automatically discover and scrape all subcategories without manual configuration.

---

## Important Notes

- ⚠️ **Slugs are deprecated** - Always use `category_url`
- ✅ URLs are in format: `https://www.boutiqaat.com/kw-ar/women/{path}/l/`
- ✅ Different locale (kw-ar vs ar-kw) in URLs is normal and correct
- ✅ The scraper validates that `category_url` exists before scraping

---

## Troubleshooting

**Problem:** "No category_url provided for 'X', SKIPPING"

**Solution:** 
1. Run `python discover_categories.py`
2. Find the category in `discovered_categories.json`
3. Copy the `category_url` to `scraping_config.py`

**Problem:** "No categories discovered"

**Solution:** Check your base category slug (should end with `/c/` like `makeup/c/`)
