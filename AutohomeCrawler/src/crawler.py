# crawler.py

import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


from src.utils import load_cookies, save_cookies, manual_login, read_json, write_json
from src.scraper import get_post_detail_links, get_post_detail
from config.settings import (
    CHROME_DRIVER_URL, COOKIES_FILE, USER_PROFILE_URL, POSTS_FILE,
    PROGRESS_FILE, COMMUNITIES, 
    WAIT_TIME, RANDOM_DELAY_RANGE, CHROME_OPTIONS, CHROME_PREFS
)

# Define paths for intermediate links file
LINKS_FILE = "data/autohome_links.json"

class AutohomeCrawler:
    def __init__(self):
        self.driver = None
        # Use dictionaries to store posts and links, keyed by community name
        self.posts = {}
        self.links = {}
        # Progress is a set of URLs of posts for which details have been scraped
        self.processed_post_urls = set()

    def _init_driver(self):
        """初始化WebDriver"""
        print("正在初始化WebDriver...")
        options = Options()
        for arg in CHROME_OPTIONS:
            options.add_argument(arg)
        if CHROME_PREFS:
            options.add_experimental_option("prefs", CHROME_PREFS)
            
        # Use webdriver_manager to handle driver executable
        service = Service(ChromeDriverManager(url=CHROME_DRIVER_URL).install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_window_size(1920, 1080)

    def _load_data_and_progress(self):
        """加载已有的数据、链接和进度"""
        print("加载数据和进度...")
        self.posts = read_json(POSTS_FILE)
        # Ensure posts structure is dictionary with lists
        if not isinstance(self.posts, dict):
             self.posts = {}
        for community_key in COMMUNITIES.keys():
             if community_key not in self.posts or not isinstance(self.posts[community_key], list):
                  self.posts[community_key] = []

        self.links = read_json(LINKS_FILE)
        # Ensure links structure is dictionary with lists
        if not isinstance(self.links, dict):
             self.links = {}
        for community_key in COMMUNITIES.keys():
             if community_key not in self.links or not isinstance(self.links[community_key], list):
                  self.links[community_key] = []

        # Load progress as a set for efficient lookups
        processed_list = read_json(PROGRESS_FILE)
        if isinstance(processed_list, list):
             self.processed_post_urls = set(processed_list)
        else:
             self.processed_post_urls = set()

        print(f"加载完成：{len(self.posts)} 个社区的数据, {sum(len(v) for v in self.links.values())} 个链接, {len(self.processed_post_urls)} 条进度记录。")

    def _save_data_and_progress(self):
        """保存抓取到的数据和进度"""
        print("保存数据和进度...")
        write_json(self.posts, POSTS_FILE)
        # Save progress as a list
        write_json(list(self.processed_post_urls), PROGRESS_FILE)
        print("保存完成。")

    def _save_links(self):
         """保存抓取到的链接"""
         print("保存链接...")
         write_json(self.links, LINKS_FILE)
         print("链接保存完成。")

    def _ensure_login(self):
        """确保用户登录"""
        print("检查登录状态...")
        # Navigate to a known page where login status can be checked implicitly via cookie loading
        # Using USER_PROFILE_URL as defined in settings
        self.driver.get(USER_PROFILE_URL)
        # load_cookies attempts to load cookies and returns True if successful
        if load_cookies(self.driver, COOKIES_FILE):
            print("Cookies加载成功，尝试验证登录状态...")
            # Optional: add a check here to see if login was successful, e.g., by checking for a logged-in element
            # For now, rely on load_cookies and manual_login logic.
            time.sleep(2) # Give some time for cookies to be applied and potential redirects
            # After loading cookies, navigate back to a relevant page or stay to check status
            # driver.get(USER_PROFILE_URL) # Might cause issues, let's rely on the next navigation
        else:
            print("Cookies文件不存在或无效，需要手动登录。")
            manual_login(self.driver, COOKIES_FILE, USER_PROFILE_URL)
            # After manual login and saving cookies, navigate again to apply cookies properly
            self.driver.get(USER_PROFILE_URL)
            time.sleep(2) # Give some time after manual login
        print("登录检查完成。")


    def scrape_links(self):
        """抓取所有社区的帖子链接"""
        print("开始抓取帖子链接...")
        
        for community_key, community_info in COMMUNITIES.items():
            url_template = community_info['url_template']
            total_pages = community_info.get('total_pages', 1)
            page_offset = community_info.get('page_offset', 0)

            print(f"开始抓取社区 {community_key} 的帖子链接...")

            for i in range(page_offset, total_pages + page_offset):
                page_num = i + 1
                # Format the URL with the current page number
                try:
                    page_url = url_template.format(page_num=page_num)
                except KeyError:
                    print(f"错误: 社区 {community_key} 的 URL 模板格式不正确: {url_template}")
                    continue # Skip this community if URL template is invalid

                print(f"抓取社区 {community_key} 的第 {page_num} 页链接...")
                
                partial_links = get_post_detail_links(self.driver, page_url, page_num, WAIT_TIME)
                
                # Append links to the community's list
                # Initialize if not exists
                if community_key not in self.links:
                     self.links[community_key] = []
                self.links[community_key].extend(partial_links)
                
                # Save links periodically or after each community/page
                self._save_links()
                print(f"社区 {community_key} 第 {page_num} 页链接已抓取并保存。")
                time.sleep(random.uniform(*RANDOM_DELAY_RANGE)) # Delay between pages
        
        print("帖子链接抓取完成。")

    def scrape_details(self):
        """抓取所有帖子的详情和回复"""
        print("开始抓取帖子详情和回复...")

        # Ensure links are loaded or scrape them first if necessary
        if not self.links or sum(len(v) for v in self.links.values()) == 0:
             print("没有链接可供抓取详情。请先运行 scrape_links。")
             return

        processed_count_session = 0

        # Iterate through all communities and their links
        for community_key, links_list in self.links.items():
            if not isinstance(links_list, list):
                 print(f"警告: 社区 {community_key} 的链接数据格式不正确，跳过详情抓取。")
                 continue

            print(f"抓取社区 {community_key} 的帖子详情...")
            for link in links_list:
                # Check if this post URL has already been processed
                if link and link not in self.processed_post_urls:
                    print(f"抓取帖子详情: {link}")
                    post_detail = get_post_detail(self.driver, link, WAIT_TIME)

                    if post_detail:
                        # Append post detail to the community's list in self.posts
                        # Initialize if not exists
                        if community_key not in self.posts:
                             self.posts[community_key] = []
                        self.posts[community_key].append(post_detail)

                        # Add the processed URL to the set
                        self.processed_post_urls.add(link)
                        processed_count_session += 1

                        # Save progress and data periodically
                        if processed_count_session % 10 == 0: # Save every 10 posts
                             self._save_data_and_progress()
                             print(f"已抓取并保存 {processed_count_session} 个帖子详情 (总计 {len(self.processed_post_urls)})。")

                        time.sleep(random.uniform(*RANDOM_DELAY_RANGE)) # Delay between posts
                    else:
                        print(f"帖子详情抓取失败或无有效内容，跳过：{link}")
                        # The get_post_detail function already saves error page
                        time.sleep(random.uniform(*RANDOM_DELAY_RANGE)) # Still add delay even if failed

                elif link in self.processed_post_urls:
                    pass # Skip if already processed
                elif not link:
                    print(f"警告: 发现一个空的帖子链接，跳过。")

        # Save remaining data and progress after loop finishes
        self._save_data_and_progress()
        print("所有帖子详情抓取完成。")

    def run(self, scrape_links=True, scrape_details=True):
        """运行爬虫

        Args:
            scrape_links (bool): Whether to scrape post links.
            scrape_details (bool): Whether to scrape post details and replies.
        """
        self._load_data_and_progress()
        self._init_driver()

        try:
            self._ensure_login()
            if scrape_links:
                self.scrape_links()
            if scrape_details:
                 # Reload data/links after scraping links, in case links file was empty initially
                 # Or if running scrape_details separately after a previous link scraping run
                 if scrape_links: # Only reload if links were potentially updated in this run
                      self._load_data_and_progress()
                 self.scrape_details()

        except Exception as e:
            print(f"爬虫运行出错: {e}")
        finally:
            if self.driver:
                self.driver.quit()
            print("爬虫运行结束。") 