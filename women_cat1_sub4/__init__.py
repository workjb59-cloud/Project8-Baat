# Boutiqaat Web Scraper Package
__version__ = '1.0.0'
__author__ = 'Boutiqaat Data Pipeline'

from .scraper import BoutiqaatScraper
from .s3_uploader import S3Uploader
from .excel_generator import ExcelGenerator

__all__ = ['BoutiqaatScraper', 'S3Uploader', 'ExcelGenerator']
