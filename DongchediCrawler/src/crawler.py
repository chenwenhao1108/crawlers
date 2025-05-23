# crawler.py

import time
import json
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Change relative imports to absolute imports based on the package structure
from src.utils import load_cookies, manual_login, load_progress, save_progress
from src.scraper import get_posts_on_page, get_replies_for_post # Add scraper import
from config.settings import (
    CHROME_DRIVER_URL, COOKIES_FILE, USER_PROFILE_URL, POSTS_FILE,
    PROGRESS_FILE, COMMUNITIES, 
    WAIT_TIME, RANDOM_DELAY_RANGE, CHROME_OPTIONS, CHROME_PREFS
)

class DongchediCrawler:
    def __init__(self):
        self.driver = None
        self.posts = {}
        # 进度现在存储所有已处理回复的帖子URL，不按社区区分
        self.processed_post_urls = []

    def _init_driver(self):
        """初始化WebDriver"""
        print("正在初始化WebDriver...")
        options = Options()
        for arg in CHROME_OPTIONS:
            options.add_argument(arg)
        if CHROME_PREFS:
            options.add_experimental_option("prefs", CHROME_PREFS)
            
        service = Service(ChromeDriverManager(url=CHROME_DRIVER_URL).install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_window_size(1920, 1080)

    def _load_data_and_progress(self):
        """加载已有的数据和进度"""
        if os.path.exists(POSTS_FILE):
            with open(POSTS_FILE, 'r', encoding='utf-8') as f:
                try:
                    self.posts = json.load(f)
                except json.JSONDecodeError:
                    self.posts = {} # Initialize if file is empty or corrupted
        else:
             # Create dummy file if it doesn't exist so json.load doesn't fail
             with open(POSTS_FILE, 'w', encoding='utf-8') as f:
                 json.dump({}, f)

        self.processed_post_urls = load_progress(PROGRESS_FILE)
        # Create dummy file if it doesn't exist so json.load doesn't fail
        if not os.path.exists(PROGRESS_FILE):
             with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                 json.dump([], f)

    def _save_data(self):
        """保存抓取到的数据"""
        with open(POSTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.posts, f, ensure_ascii=False, indent=4)

    def _save_progress(self):
        """保存抓取进度"""
        save_progress(PROGRESS_FILE, self.processed_post_urls)

    def _ensure_login(self):
        """确保用户登录"""
        self.driver.get(USER_PROFILE_URL)
        if not load_cookies(self.driver, COOKIES_FILE):
            manual_login(self.driver, COOKIES_FILE, USER_PROFILE_URL)
        self.driver.get(USER_PROFILE_URL) # Navigate back after loading cookies
        time.sleep(2) # Give some time for cookies to be applied

    def scrape_posts(self):
        """抓取帖子列表"""
        print("开始抓取所有社区的帖子列表...")
        
        for community_key, community_info in COMMUNITIES.items():
            community_url = community_info['url']
            total_pages = community_info.get('total_pages', 1) # Default to 1 page if not specified
            page_offset = community_info.get('page_offset', 0) # Default to 0 offset if not specified

            print(f"开始抓取社区: {community_key}")

            # Initialize list for the community if it doesn't exist
            if community_key not in self.posts:
                self.posts[community_key] = []

            # Determine starting page based on existing data for this community
            # Assuming each entry in self.posts[community_key] corresponds to one page of posts
            # This might need refinement if your original script didn't save data page by page
            # Let's assume for simplicity here that the number of collected post lists corresponds to pages scraped
            start_page_for_community = page_offset + len(self.posts[community_key])

            if start_page_for_community > total_pages + page_offset:
                 print(f"社区 {community_key} 的帖子列表已全部抓取。")
                 continue

            print(f"从社区 {community_key} 的第 {start_page_for_community + 1} 页开始抓取...")

            for i in range(start_page_for_community, total_pages + page_offset):
                # Assuming URL format is base_url/page_number
                page_url = f"{community_url}/{i + 1}"
                posts_on_page = get_posts_on_page(self.driver, page_url, WAIT_TIME)
                
                # Append posts from this page as a new list entry for this community
                # This assumes you want to keep track of posts per page. 
                # If you just want a flat list of all posts for the community, 
                # change extend logic here.
                # Let's stick to the original structure of appending list of posts
                self.posts[community_key].extend(posts_on_page)
                
                self._save_data()
                print(f"社区 {community_key} 的第 {i + 1} 页数据已抓取并保存。")
                time.sleep(random.uniform(*RANDOM_DELAY_RANGE))

    def scrape_replies(self):
        """抓取帖子回复"""
        print("开始抓取所有帖子的回复...")
        
        # Iterate through all communities and their posts
        for community_key, posts_list in self.posts.items():
            if not isinstance(posts_list, list):
                print(f"警告: 社区 {community_key} 的数据格式不正确，跳过抓取回复。")
                continue

            print(f"抓取社区 {community_key} 的帖子回复...")
            for post in posts_list:
                url = post.get('url')
                # Check if the URL has already been processed for replies
                if url and url not in self.processed_post_urls:
                    replies = get_replies_for_post(self.driver, url, WAIT_TIME)
                    post['replies'].extend(replies)
                    print(f"帖子 {url} 的回复已抓取。")
                    self.processed_post_urls.append(url)
                    self._save_data()
                    self._save_progress()
                    time.sleep(random.uniform(*RANDOM_DELAY_RANGE))
                elif url and url in self.processed_post_urls:
                    print(f"帖子 {url} 的回复已跳过 (已在进度中)。")
                elif not url:
                    print(f"警告: 发现一个没有URL的帖子，跳过抓取回复。")

    def run(self):
        """运行爬虫"""
        self._load_data_and_progress()
        self._init_driver()
        self._ensure_login()

        try:
            self.scrape_posts() # Uncomment to scrape posts
            self.scrape_replies() # Uncomment to scrape replies
        except Exception as e:
            print(f"爬虫运行出错: {e}")
        finally:
            if self.driver:
                self.driver.quit()
            print("爬虫运行结束。") 