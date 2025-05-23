# scraper.py

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Use absolute import for utils and settings
# from .utils import to_timestamp, scroll_to_bottom, save_error_page # Import necessary utils functions
# from ..config.settings import BASE_URL, WAIT_TIME, SCROLL_WAIT_TIME # Import necessary settings
from src.utils import to_timestamp, scroll_to_bottom, save_error_page # Import necessary utils functions
from config.settings import BASE_URL, WAIT_TIME, SCROLL_WAIT_TIME # Import necessary settings


def get_post_detail_links(driver, url, page_num, time_out=WAIT_TIME):
    """抓取单页的帖子详情链接"""
    links = []
    try:
        driver.get(url)
        wait = WebDriverWait(driver, time_out)
        print(f"正在抓取页面链接: {url}")
        
        # 等待页面基本元素加载完成
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        scroll_to_bottom(driver, wait_time=SCROLL_WAIT_TIME)
        
        max_retries = 3
        retries = 0
        while retries < max_retries:
            try:
                print(f"尝试获取第 {page_num} 页链接 (重试 {retries + 1}/{max_retries})...")
                
                # Use the provided XPath to find list items
                linkListItems = wait.until(EC.presence_of_all_elements_located(
                    (By.XPATH, "//ul[contains(@class, 'post-list')]/li[not(contains(@class, 'video-type'))]")))

                if not linkListItems:
                    print(f"页面 {url} 未找到帖子列表项。")
                    break # Exit retry loop if no items found

                for listItem in linkListItems:
                    # Find the anchor tag with the title within the list item
                    try:
                         aElement = listItem.find_element(By.XPATH, ".//p[contains(@class, 'post-title')]/a")
                         href = aElement.get_attribute("href")
                         if href:
                             # Ensure it's a full URL
                             if not href.startswith('http'):
                                 href = BASE_URL + href
                             links.append(href)
                    except Exception as e:
                        print(f"在列表项中查找链接时出错: {e}")
                        continue # Continue to the next list item
                
                print(f"页面 {url} 抓取到 {len(links)} 个帖子链接.")
                break # Exit retry loop on success

            except Exception as e:
                print(f"获取页面 {url} 链接失败 (重试 {retries + 1}/{max_retries}):\n{e}")
                retries += 1
                time.sleep(random.uniform(1, 3)) # Wait before retry
                scroll_to_bottom(driver, SCROLL_WAIT_TIME)  # Retry by scrolling again
        else:
            print(f"尝试 {max_retries} 次后仍无法获取页面 {url} 的链接。")
            save_error_page(driver, url)
            
    except Exception as e:
        print(f'获取页面 {url} 链接失败:\n{e}')
        if driver:
            save_error_page(driver, url)

    finally:
        return links


def get_post_detail(driver, url, time_out=WAIT_TIME):
    """抓取单个帖子详情（包括回复）"""
    post_detail = None
    try:
        driver.get(url)
        wait = WebDriverWait(driver, time_out)
        print(f"正在抓取帖子详情: {url}")
        
        # 等待页面基本元素加载完成
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        scroll_to_bottom(driver, wait_time=SCROLL_WAIT_TIME) # Scroll to load all content/replies
        
        # Use BeautifulSoup for parsing after scrolling
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract post details
        username_element = soup.select_one(".user-name")
        timestamp_element = soup.select_one(".post-handle-publish")
        title_element = soup.select_one(".post-title")
        content_elements = soup.select(".tz-paragraph")
        
        username = username_element.text.strip() if username_element else '无用户名'
        
        timestamp_str = timestamp_element.text.strip() if timestamp_element else '无时间戳'
        timestamp = to_timestamp(timestamp_str)

        title = title_element.text.strip() if title_element else '无标题'
        content = '\n'.join([elem.text.strip() for elem in content_elements]) if content_elements else '无内容'
        
        # Combine title and content if needed, based on original script's approach
        full_content = f"{title}\n{content}" if title and content != '无内容' else content if content != '无内容' else title
        if full_content == '无内容' and title == '无标题':
             full_content = '无内容或标题'
        elif full_content == '无内容' and title != '无标题':
             full_content = title


        if not full_content or full_content == '无内容或标题':
            print(f"帖子 {url} 未抓取到有效内容，跳过。")
            # save_error_page(driver, url) # Optionally save page if content is missing
            return None # Skip if no content

        post_detail = {
            'url': url,
            "timestamp": timestamp,
            "username": username,
            "content": full_content,
            "replies": []
        }

        # Extract replies
        # Use more specific selectors if necessary, based on your observation of AutoHome HTML
        # The original script used: .reply-detail and .reply-static-text.fn-fl:not(.fn-hide)
        reply_elements = soup.select('.reply-detail')
        reply_time_elements = soup.select('.reply-static-text.fn-fl:not(.fn-hide)')

        replies = []
        # Ensure both lists have the same length before zipping to avoid errors
        min_replies_count = min(len(reply_elements), len(reply_time_elements))

        for i in range(min_replies_count):
             reply_elem = reply_elements[i]
             reply_time_elem = reply_time_elements[i]

             reply_content = reply_elem.text.strip()
             reply_time_str = reply_time_elem.text.strip()
             reply_time = to_timestamp(reply_time_str)
             
             if reply_content:
                 replies.append({
                     "content": reply_content,
                     "timestamp": reply_time
                 })

        post_detail['replies'] = replies
        print(f"帖子 {url} 抓取到 {len(replies)} 条回复。")

    except Exception as e:
        print(f'抓取帖子详情失败 {url}:\n{e}')
        save_error_page(driver, url) # Save page on error
        return None

    finally:
        return post_detail 