# run.py

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from crawler import DongchediCrawler

if __name__ == "__main__":
    crawler = DongchediCrawler()
    crawler.run() 