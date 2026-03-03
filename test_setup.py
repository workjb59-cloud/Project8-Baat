#!/usr/bin/env python
"""
Simple test script to verify the installation and configuration
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    try:
        import requests
        print("  ✓ requests")
        
        import bs4
        print("  ✓ beautifulsoup4")
        
        import boto3
        print("  ✓ boto3")
        
        import openpyxl
        print("  ✓ openpyxl")
        
        import pandas
        print("  ✓ pandas")
        
        import playwright
        print("  ✓ playwright")
        
        from women_cat1.scraper import BoutiqaatScraper
        print("  ✓ BoutiqaatScraper")
        
        from women_cat1.s3_uploader import S3Uploader
        print("  ✓ S3Uploader")
        
        from women_cat1.excel_generator import ExcelGenerator
        print("  ✓ ExcelGenerator")
        
        from women_cat1.main import BoutiqaatDataPipeline
        print("  ✓ BoutiqaatDataPipeline")
        
        print("✅ All imports successful!\n")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {str(e)}\n")
        return False


def test_aws_credentials():
    """Test AWS credentials"""
    print("🔍 Testing AWS credentials...")
    try:
        from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET
        
        if not AWS_ACCESS_KEY_ID:
            print("  ⚠️  AWS_ACCESS_KEY_ID not set")
            return False
        print("  ✓ AWS_ACCESS_KEY_ID is set")
        
        if not AWS_SECRET_ACCESS_KEY:
            print("  ⚠️  AWS_SECRET_ACCESS_KEY not set")
            return False
        print("  ✓ AWS_SECRET_ACCESS_KEY is set")
        
        if not AWS_S3_BUCKET:
            print("  ⚠️  AWS_S3_BUCKET not set")
            return False
        print(f"  ✓ AWS_S3_BUCKET: {AWS_S3_BUCKET}")
        
        print("✅ AWS credentials configured!\n")
        return True
    except Exception as e:
        print(f"❌ AWS configuration failed: {str(e)}\n")
        return False


def test_s3_connection():
    """Test S3 connection"""
    print("🔍 Testing S3 connection...")
    try:
        from women_cat1.s3_uploader import S3Uploader
        uploader = S3Uploader()
        
        if uploader.test_connection():
            print("✅ S3 connection successful!\n")
            return True
        else:
            print("❌ S3 connection failed!\n")
            return False
    except Exception as e:
        print(f"❌ S3 test failed: {str(e)}\n")
        return False


def test_website_access():
    """Test if website is accessible"""
    print("🔍 Testing website access...")
    try:
        import requests
        response = requests.get('https://www.boutiqaat.com/', timeout=10)
        if response.status_code == 200:
            print("✅ Website is accessible!\n")
            return True
        else:
            print(f"❌ Website returned status {response.status_code}\n")
            return False
    except Exception as e:
        print(f"⚠️  Could not access website: {str(e)}\n")
        print("   This might be due to network issues or website blocking\n")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("Boutiqaat Scraper - Configuration Test")
    print("=" * 50)
    print()
    
    results = {
        'Imports': test_imports(),
        'AWS Credentials': test_aws_credentials(),
        'S3 Connection': test_s3_connection(),
        'Website Access': test_website_access(),
    }
    
    print("=" * 50)
    print("Test Summary:")
    print("=" * 50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print("=" * 50)
    print(f"Result: {passed}/{total} tests passed")
    print()
    
    if passed == total:
        print("🎉 All systems ready! You can now run:")
        print("   python -m src.main")
        print()
        return 0
    else:
        print("⚠️  Some tests failed. Please address the issues above.")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
