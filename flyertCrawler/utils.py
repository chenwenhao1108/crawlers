import pickle
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from pprint import pprint
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import json


cookies_file = "cookies.pkl"

def parse_timestamp(time_str):
    if not time_str:
        return None
        
    # 尝试提取日期时间信息
    date_pattern = r'(\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2})'
    days_ago_pattern = r'(\d+)\s*天前'
    hours_ago_pattern = r'(\d+)\s*小时前'
    yesterday_pattern = r'昨天\s*(\d{1,2}:\d{1,2})'
    before_yesterday_pattern = r'前天\s*(\d{1,2}:\d{1,2})'
    just_now_pattern = r'刚刚'
    
    # 清理字符串，移除地区信息
    # time_str = re.sub(r'\s+[^\s\d:-]+$', '', time_str)  # 移除末尾的地区信息
    
    # 搜索完整的日期时间格式
    date_match = re.search(date_pattern, time_str)
    if date_match:
        try:
            return datetime.strptime(date_match.group(1), '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
        except ValueError:
            pass
    
    # 搜索"前天 HH:MM"格式
    before_yesterday_match = re.search(before_yesterday_pattern, time_str)
    if before_yesterday_match:
        try:
            time_str = before_yesterday_match.group(1)
            before_yesterday = datetime.now() - timedelta(days=2)
            full_time = f"{before_yesterday.strftime('%Y-%m-%d')} {time_str}"
            return datetime.strptime(full_time, '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
        except ValueError:
            pass
    
    # 搜索"昨天 HH:MM"格式
    yesterday_match = re.search(yesterday_pattern, time_str)
    if yesterday_match:
        try:
            time_str = yesterday_match.group(1)
            yesterday = datetime.now() - timedelta(days=1)
            full_time = f"{yesterday.strftime('%Y-%m-%d')} {time_str}"
            return datetime.strptime(full_time, '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
        except ValueError:
            pass
            
    # 搜索"x小时前"格式
    hours_match = re.search(hours_ago_pattern, time_str)
    if hours_match:
        try:
            hours = int(hours_match.group(1))
            timestamp = datetime.now() - timedelta(hours=hours)
            return timestamp.strftime('%Y-%m-%d %H:%M')
        except ValueError:
            pass
    
    # 搜索"x天前"格式
    days_match = re.search(days_ago_pattern, time_str)
    if days_match:
        try:
            days = int(days_match.group(1))
            timestamp = datetime.now() - timedelta(days=days)
            return timestamp.strftime('%Y-%m-%d %H:%M')
        except ValueError:
            pass
    
    # 搜索"刚刚"格式
    if re.search(just_now_pattern, time_str):
        return datetime.now().strftime('%Y-%m-%d %H:%M')
            
    return None  # 如果无法解析，返回None


def save_cookies(driver, cookies_file):
    with open(cookies_file, 'wb') as f:
        pickle.dump(driver.get_cookies(), f)

def load_cookies(driver, cookies_file):
    print("检查cookies文件...")
    if os.path.exists(cookies_file):
        print("找到cookies文件，正在加载...")
        
        with open(cookies_file, 'rb') as f:
            cookies = pickle.load(f)
        try:
            for cookie in cookies:
                driver.add_cookie(cookie)
            print("Cookies加载成功")
            driver.refresh()
            return True
        except Exception as e:
            pprint(cookie)
            print(f"current url: {driver.current_url}")
            print(f"加载cookies时出错: {e}")
            return False
    print("未找到cookies文件")
    return False

def manual_login(driver, cookies_file):
    driver.get('https://www.flyert.com.cn/home.php?mod=spacecp&ac=profile')
    input("请登录，登录成功跳转后，按回车键继续...")
    save_cookies(driver, cookies_file)  # 登录后保存cookie到本地
    print("程序正在继续运行")

def test_cookies():
    # 首次登录获取cookie文件
    print("测试cookies文件是否已获取。若无，请在弹出的窗口中登录，登录完成后，窗口将关闭；若有，窗口会立即关闭")
    driver = webdriver.Chrome(service=Service('chromedriver-win64/chromedriver.exe'))
    driver.get('https://www.flyert.com.cn/')
    if not load_cookies(driver, cookies_file):
        manual_login(driver, cookies_file)
    driver.quit()
    
def scroll_to_bottom(driver, wait_time=3):
    """渐进式滚动到页面底部，模拟真实用户行为"""
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # 滚动一小段距离
        for i in range(3):
            current_height = last_height // 3 * (i + 1)
            driver.execute_script(f"window.scrollTo(0, {current_height});")
            time.sleep(random.uniform(0.5, 1))
            
        # 等待页面加载
        time.sleep(wait_time)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        
def save_error_page(driver, url, page_num = None):
    """保存错误页面源码的辅助函数"""
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        url_div = soup.new_tag("div", style="font-weight: bold; margin-bottom: 20px;")
        url_div.string = f"Page URL: {url}"
        
        if soup.body:
            soup.body.insert(0, url_div)
        else:
            soup.append(url_div)
        
        if page_num:
            filename_base = f"{url.rsplit('/', 1)[-1]}_page_{page_num}"
        else:
            filename_base = url.rsplit('/', 1)[-1]
        output_folder = "error_pages"
        os.makedirs(output_folder, exist_ok=True)
        
        file_path = os.path.join(output_folder, f'{filename_base}.html')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(soup.prettify()) #type: ignore
            
    except Exception as e:
        print(f"Failed to save error page: {e}")
        
class ProgressManager:
    def __init__(self, progress_file='data/progress.json'):
        self.progress_file = progress_file
        self.progress = self._load_progress()
        
    def _load_progress(self):
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                "current_hotel": "",
                "processed_links": [],
                "error_links": [],
                "empty_links": []
            }
    
    def save_progress(self):
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=4)
    
    def is_link_processed(self, link):
        return link in self.progress['processed_links'] or link in self.progress['error_links'] or link in self.progress['empty_links']
    
    def mark_link_processed(self, link):
        if link not in self.progress['processed_links']:
            self.progress['processed_links'].append(link)
        if link in self.progress['error_links']:
            self.progress['error_links'].remove(link)
        self.save_progress()
    
    def mark_error_link(self, link):
        if link not in self.progress['error_links']:
            self.progress['error_links'].append(link)
            self.save_progress()
            
    def mark_empty_link(self, link):
        if link not in self.progress['empty_links']:
            self.progress['empty_links'].append(link)
        if link in self.progress['error_links']:
            self.progress['error_links'].remove(link)
        self.save_progress()
    
    def set_current_hotel(self, hotel):
        self.progress['current_hotel'] = hotel
        self.save_progress()
    
    def get_current_hotel(self):
        return self.progress['current_hotel']
    
def main():
    test_timeStrs = [
        '3 小时前',
        '3 天前',
    ]
    for time_str in test_timeStrs:
        print(f"原始时间字符串: {time_str}")
        parsed_time = parse_timestamp(time_str)
        if parsed_time:
            print(f"解析后的时间: {parsed_time}")
        else:
            print("无法解析时间")
            
if __name__ == "__main__":
    main()