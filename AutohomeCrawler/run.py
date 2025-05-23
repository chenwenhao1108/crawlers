# run.py

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from crawler import AutohomeCrawler

if __name__ == "__main__":
    crawler = AutohomeCrawler()
    # By default, scrape links and then details
    crawler.run(scrape_links=True, scrape_details=True)

    # You can choose to run only one step if needed:
    # crawler.run(scrape_links=True, scrape_details=False) # Only scrape links
    # crawler.run(scrape_links=False, scrape_details=True) # Only scrape details (requires links in data/autohome_links.json) 