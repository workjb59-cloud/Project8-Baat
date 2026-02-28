#!/usr/bin/env python3
"""
Test script to verify configuration and connectivity
Run this before starting the full scraper to catch issues early
"""
import sys
import os

def test_imports():
    """Test that all required packages are installed"""
    print("\n" + "=" * 80)
    print("TESTING IMPORTS")
    print("=" * 80 + "\n")
    
    required_packages = [
        ('scrapling', 'Scrapling'),
        ('boto3', 'Boto3 (AWS SDK)'),
        ('pandas', 'Pandas'),
        ('openpyxl', 'OpenPyXL'),
        ('PIL', 'Pillow'),
        ('dotenv', 'Python-dotenv'),
        ('tqdm', 'tqdm'),
        ('requests', 'Requests'),
    ]
    
    all_good = True
    for module_name, display_name in required_packages:
        try:
            __import__(module_name)
            print(f"✓ {display_name}")
        except ImportError:
            print(f"❌ {display_name} - NOT INSTALLED")
            all_good = False
    
    if not all_good:
        print("\n❌ Some packages are missing!")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✓ All required packages are installed")
    return True


def test_env_file():
    """Test that environment configuration is available"""
    print("\n" + "=" * 80)
    print("TESTING ENVIRONMENT CONFIGURATION")
    print("=" * 80 + "\n")
    
    from pathlib import Path
    from dotenv import load_dotenv
    
    # Check if running in GitHub Actions
    is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
    
    if is_github_actions:
        print("✓ Running in GitHub Actions environment")
        print("  Environment variables loaded from GitHub secrets")
    else:
        env_file = Path('.env')
        if env_file.exists():
            print("✓ .env file exists (local development)")
        else:
            print("⚠️  .env file not found (using environment variables)")
        
        # Load environment variables
        load_dotenv()
    
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
    ]
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '****'
            print(f"✓ {var} = {masked}")
        else:
            print(f"❌ {var} - NOT SET")
            all_good = False
    
    # Optional variables
    optional_vars = {
        'AWS_REGION': 'us-east-1',
        'S3_BUCKET_NAME': 'boutiqaat-data',
    }
    
    for var, default in optional_vars.items():
        value = os.getenv(var, default)
        print(f"  {var} = {value}")
    
    if not all_good:
        print("\n❌ Some required environment variables are missing!")
        if not is_github_actions:
            print("Create a .env file or set environment variables.")
        else:
            print("Configure GitHub secrets in: Settings → Secrets and variables → Actions")
        return False
    
    print("\n✓ Environment variables configured")
    return True


def test_aws_connection():
    """Test AWS S3 connection"""
    print("\n" + "=" * 80)
    print("TESTING AWS S3 CONNECTION")
    print("=" * 80 + "\n")
    
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        bucket_name = os.getenv('S3_BUCKET_NAME', 'boutiqaat-data')
        
        # Test bucket access
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✓ Successfully connected to S3 bucket: {bucket_name}")
            
            # Try to list objects (just to verify write permissions)
            response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
            print("✓ Have read access to bucket")
            
            # Test write permission with a test file
            test_key = 'test_connection.txt'
            test_content = b'Connection test'
            
            try:
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=test_key,
                    Body=test_content
                )
                print("✓ Have write access to bucket")
                
                # Clean up test file
                s3_client.delete_object(Bucket=bucket_name, Key=test_key)
                print("✓ Have delete access to bucket")
                
            except ClientError as e:
                print(f"⚠️  Limited permissions: {e}")
                print("   (Write/delete permissions may be restricted)")
            
            print("\n✓ AWS S3 connection successful")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"⚠️  Bucket '{bucket_name}' does not exist")
                print("   The scraper will attempt to create it when run")
                return True
            else:
                print(f"❌ Error accessing bucket: {e}")
                return False
                
    except NoCredentialsError:
        print("❌ AWS credentials not found or invalid")
        return False
    except Exception as e:
        print(f"❌ Error connecting to AWS: {e}")
        return False


def test_scraping_config():
    """Test scraping configuration"""
    print("\n" + "=" * 80)
    print("TESTING SCRAPING CONFIGURATION")
    print("=" * 80 + "\n")
    
    try:
        from scraping_config import get_categories, get_brands, get_celebrities
        
        categories = get_categories()
        brands = get_brands()
        celebrities = get_celebrities()
        
        print(f"✓ Categories configured: {len(categories)}")
        if categories:
            print(f"  Example: {categories[0]['name']} ({categories[0]['slug']})")
        
        print(f"✓ Brands configured: {len(brands)}")
        if brands:
            print(f"  Example: {brands[0]['name']} ({brands[0]['slug']})")
        
        print(f"✓ Celebrities configured: {len(celebrities)}")
        if celebrities:
            print(f"  Example: {celebrities[0]['name']} ({celebrities[0]['slug']})")
        
        total = len(categories) + len(brands) + len(celebrities)
        if total == 0:
            print("\n⚠️  WARNING: No items configured to scrape!")
            print("Edit scraping_config.py to add items")
            return False
        
        print(f"\n✓ Total items to scrape: {total}")
        return True
        
    except ImportError:
        print("⚠️  scraping_config.py not found")
        print("   Will use default sample configuration")
        return True
    except Exception as e:
        print(f"❌ Error loading scraping config: {e}")
        return False


def test_single_scrape():
    """Test scraping a single page"""
    print("\n" + "=" * 80)
    print("TESTING SCRAPING (Single Page)")
    print("=" * 80 + "\n")
    
    try:
        from scraper import BoutiqaatScraper
        
        scraper = BoutiqaatScraper()
        
        # Test with a known category
        print("Attempting to scrape foundations category...")
        products = scraper.scrape_category('makeup/foundations/l')
        
        if products:
            print(f"✓ Successfully scraped {len(products)} products")
            print(f"\n  Example product:")
            print(f"    Name: {products[0].get('name', 'N/A')}")
            print(f"    Brand: {products[0].get('brand_name', 'N/A')}")
            print(f"    Price: {products[0].get('final_price', 'N/A')} {products[0].get('currency_code', '')}")
            return True
        else:
            print("⚠️  No products found (page structure may have changed)")
            return False
            
    except Exception as e:
        print(f"❌ Error testing scraper: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("BOUTIQAAT SCRAPER - CONFIGURATION TEST")
    print("=" * 80)
    
    results = {
        'imports': test_imports(),
        'env': test_env_file(),
        'aws': test_aws_connection(),
        'config': test_scraping_config(),
        'scrape': test_single_scrape(),
    }
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80 + "\n")
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{test_name.upper():<15} {status}")
    
    all_pass = all(results.values())
    
    print("\n" + "=" * 80)
    if all_pass:
        print("✓ ALL TESTS PASSED")
        print("=" * 80)
        print("\nYou're ready to run the scraper!")
        print("Run: python run.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 80)
        print("\nPlease fix the issues above before running the scraper.")
        print("Check the error messages for guidance.")
    
    print("\n")
    
    sys.exit(0 if all_pass else 1)


if __name__ == '__main__':
    main()
