# scraper.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


from .utils import parse_time_string, scroll_to_bottom
from config.settings import BASE_URL, WAIT_TIME, SCROLL_WAIT_TIME # Import necessary settings


def get_posts_on_page(driver, url, wait_time=WAIT_TIME):
    """抓取单页的帖子列表信息"""
    posts = []
    try:
        driver.get(url)
        wait = WebDriverWait(driver, wait_time)
        print(f"正在抓取页面: {url}")
        
        # 等待页面基本元素加载完成
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # 执行渐进式滚动
        scroll_to_bottom(driver, wait_time=2)
        
        print("开始解析页面内容...")
        
        # 使用BeautifulSoup解析页面源
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # 定位帖子元素
        articles = soup.select('section > div > p > a') # Simplified selector based on previous code

        for article in articles:
            link = article.get('href')
            if link and '/ugc/article/' in link: # Ensure it's a post link
                # Attempt to find associated elements relative to the link or its parent
                # This part might need adjustment based on the actual HTML structure
                parent_div = article.find_parent('section')
                if parent_div:
                    content_element = parent_div.select_one('.jsx-81802501.jsx-2089696349.tw-text-common-black')
                    username_element = parent_div.select_one('.tw-text-16.tw-text-black')
                    timestamp_element = parent_div.select_one('.jsx-1875074220.tw-text-video-shallow-gray.tw-flex-none')

                    content = content_element.text.strip() if content_element else None
                    username = username_element.text.strip() if username_element else '无用户名'
                    # Use parse_time_string for timestamp
                    timestamp_str = timestamp_element.text.strip() if timestamp_element else '无时间戳'
                    timestamp = parse_time_string(timestamp_str)

                    if content and link:
                        # Construct full URL
                        full_url = BASE_URL + link
                        posts.append({
                            'url': full_url,
                            "timestamp": timestamp,
                            "username": username,
                            "content": content,
                            "replies": []
                        })

        print(f"页面 {url} 抓取到 {len(posts)} 个帖子.")

    except Exception as e:
        print(f'抓取页面 {url} 失败: {e}')

    finally:
        return posts


def get_replies_for_post(driver, url, wait_time=WAIT_TIME):
    """抓取单个帖子的回复信息"""
    replies = []
    try:
        # Use the full URL directly
        driver.get(url)
        wait = WebDriverWait(driver, wait_time)
        print(f"正在抓取帖子回复: {url}")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        # Use SCROLL_WAIT_TIME from settings
        scroll_to_bottom(driver, wait_time=SCROLL_WAIT_TIME) # Scroll to load replies
        
        # Using BeautifulSoup for parsing after scrolling
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Select reply elements and timestamp elements
        reply_elements = soup.select('span.tw-text-common-black')
        timestamp_elements = soup.select('span.tw-text-video-shallow-gray.tw-flex-none')
        
        # Filter elements to ensure they are part of a reply block if necessary
        # This might need refinement based on precise HTML structure

        if not reply_elements:
            print(f"帖子 {url} 未抓取到回复或抓取失败。")
            return replies

        for reply_element, timestamp_element in zip(reply_elements, timestamp_elements):
            reply = {
                'content': reply_element.text.strip(),
                'timestamp': parse_time_string(timestamp_element.text.strip())
            }
            replies.append(reply)

        print(f"帖子 {url} 抓取到 {len(replies)} 条回复。")

    except Exception as e:
        print(f'抓取帖子回复失败 {url}: {e}')

    finally:
        return replies 