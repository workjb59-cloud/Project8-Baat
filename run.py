#!/usr/bin/env python3
"""
Simple runner script for Boutiqaat Scraper
Just run: python run.py
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_environment():
    """Check if environment is properly configured"""
    import os
    from pathlib import Path
    
    print("Checking environment...")
    
    # Check if .env exists
    env_file = Path('.env')
    if not env_file.exists():
        print("\n⚠️  WARNING: .env file not found!")
        print("Please create .env file with your AWS credentials.")
        print("You can copy .env.example as a template:")
        print("\n    cp .env.example .env")
        print("\nThen edit .env and add your AWS credentials.")
        
        response = input("\nDo you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(1)
    else:
        print("✓ .env file found")
    
    # Check if scraping_config.py exists
    config_file = Path('scraping_config.py')
    if not config_file.exists():
        print("⚠️  WARNING: scraping_config.py not found!")
        print("Using default sample configuration.")
    else:
        print("✓ scraping_config.py found")
    
    # Try to import required packages
    try:
        import scrapling
        print("✓ scrapling installed")
    except ImportError:
        print("❌ scrapling not installed!")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    try:
        import boto3
        print("✓ boto3 installed")
    except ImportError:
        print("❌ boto3 not installed!")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    try:
        import pandas
        print("✓ pandas installed")
    except ImportError:
        print("❌ pandas not installed!")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    print("\n✓ Environment check passed!\n")
    return True


def show_configuration():
    """Show what will be scraped"""
    try:
        from scraping_config import get_categories, get_brands, get_celebrities
        
        categories = get_categories()
        brands = get_brands()
        celebrities = get_celebrities()
        
        print("=" * 80)
        print("SCRAPING CONFIGURATION")
        print("=" * 80)
        print(f"\nCategories to scrape: {len(categories)}")
        if categories:
            for i, cat in enumerate(categories[:5], 1):
                print(f"  {i}. {cat['name']}")
            if len(categories) > 5:
                print(f"  ... and {len(categories) - 5} more")
        
        print(f"\nBrands to scrape: {len(brands)}")
        if brands:
            for i, brand in enumerate(brands[:5], 1):
                print(f"  {i}. {brand['name']}")
            if len(brands) > 5:
                print(f"  ... and {len(brands) - 5} more")
        
        print(f"\nCelebrities to scrape: {len(celebrities)}")
        if celebrities:
            for i, celeb in enumerate(celebrities[:5], 1):
                print(f"  {i}. {celeb['name']}")
            if len(celebrities) > 5:
                print(f"  ... and {len(celebrities) - 5} more")
        
        print("\n" + "=" * 80)
        
        total = len(categories) + len(brands) + len(celebrities)
        if total == 0:
            print("\n⚠️  WARNING: No items configured to scrape!")
            print("Please edit scraping_config.py to add categories, brands, or celebrities.")
            sys.exit(1)
        
        return True
        
    except ImportError:
        print("Using default sample configuration")
        return True


def main():
    """Main entry point"""
    print("\n" + "=" * 80)
    print("BOUTIQAAT SCRAPER")
    print("=" * 80 + "\n")
    
    # Check environment
    if not check_environment():
        return
    
    # Show configuration
    show_configuration()
    
    # Confirm before starting
    print("\nThis will scrape Boutiqaat and upload data to S3.")
    print("This may take several minutes to hours depending on the configuration.")
    
    response = input("\nDo you want to start scraping? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled by user.")
        return
    
    print("\n" + "=" * 80)
    print("STARTING SCRAPER...")
    print("=" * 80 + "\n")
    
    # Run the main pipeline
    from main import main as run_pipeline
    
    try:
        results = run_pipeline()
        
        print("\n" + "=" * 80)
        print("✓ SCRAPING COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nResults have been saved to S3 and a JSON summary file.")
        print("Check the logs for detailed information.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ ERROR OCCURRED")
        print("=" * 80)
        print(f"\nError: {e}")
        print("\nCheck boutiqaat_scraper.log for detailed error information.")
        sys.exit(1)


if __name__ == '__main__':
    main()
