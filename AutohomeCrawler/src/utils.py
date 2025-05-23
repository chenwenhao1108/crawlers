import json
import os
import pickle
import time
import random
from datetime import datetime, timedelta
import re

from bs4 import BeautifulSoup

# File read/write functions
def read_json(file_path):
    """读取JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
        return {} # Return empty dict for new files
    except json.JSONDecodeError as e:
        print(f"解码JSON出错: {e}")
        return {} # Return empty dict if file is corrupted
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return {}

    
def write_json(data, file_path):
    """写入JSON文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"写入文件时出错: {e}")

# Time parsing function
def to_timestamp(time_str):
    """将汽车之家的各种时间字符串转换为时间戳"""
    # 匹配 "x小时前"，不限定位置，取最后一个匹配项
    hour_matches = list(re.finditer(r'(\d+)小时前', time_str))
    if hour_matches:
        hours_ago = int(hour_matches[-1].group(1))  # 取最后一个匹配
        return int((datetime.now() - timedelta(hours=hours_ago)).timestamp())

    # 匹配 "x天前"
    day_matches = list(re.finditer(r'(\d+)天前', time_str))
    if day_matches:
        days_ago = int(day_matches[-1].group(1))
        return int((datetime.now() - timedelta(days=days_ago)).timestamp())

    # 匹配标准时间格式 yyyy-mm-dd hh:mm:ss（必须出现在字符串结尾）
    date_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$', time_str)
    if date_match:
        dt_str = date_match.group(1)
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            return int(dt.timestamp())
        except ValueError:
            pass  # 如果转换失败，则继续到下一步

    # 都不匹配则返回原字符串或者None，取决于需求。这里返回原字符串以便调试。
    return time_str

# Cookie handling functions
def save_cookies(driver, cookies_file):
    """保存cookie到文件"""
    try:
        with open(cookies_file, 'wb') as f:
            pickle.dump(driver.get_cookies(), f)
    except Exception as e:
        print(f"保存cookie失败: {e}")

def load_cookies(driver, cookies_file):
    """从文件加载cookie并添加到WebDriver"""
    if os.path.exists(cookies_file):
        try:
            with open(cookies_file, 'rb') as f:
                cookies = pickle.load(f)
            for cookie in cookies:
                # Check if domain is valid before adding cookie
                # AutoHome cookies might have specific domains, handle potential exceptions
                try:
                    if 'domain' in cookie and cookie['domain']:
                         # Ensure domain is valid for the current driver URL
                         # A simple check, more robust logic might be needed depending on site
                        if driver.current_url and cookie['domain'] in driver.current_url:
                             driver.add_cookie(cookie)
                        elif not cookie['domain']:
                             # Add cookies without domain if allowed/needed
                             driver.add_cookie(cookie)

                except Exception as e:
                    print(f"添加cookie时出错: {e}")
                    continue # Continue with other cookies
            print("Cookies已加载。")
            return True
        except Exception as e:
            print(f"加载cookie失败: {e}")
            return False
    return False

def manual_login(driver, cookies_file, user_profile_url):
    """引导用户手动登录并保存cookie"""
    print("Cookies文件不存在或加载失败，请手动登录。")
    driver.get(user_profile_url)
    input("请登录，登录成功或到达用户主页后，按回车键继续...")
    save_cookies(driver, cookies_file)  # 登录后保存cookie到本地
    print("程序正在继续运行")

# Scrolling function
def scroll_to_bottom(driver, wait_time=1):
    """渐进式滚动到页面底部，模拟真实用户行为"""
    print("正在滚动页面...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # 滚动一小段距离
        for i in range(3):
            current_height = last_height // 3 * (i + 1)
            driver.execute_script(f"window.scrollTo(0, {current_height});")
            time.sleep(random.uniform(0.5, 1))
            
        # 等待页面加载
        # time.sleep(wait_time) # AutoHome might not need extra wait here based on original code
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    print("滚动完成。")

# Error page saving
def save_error_page(driver, url):
    """保存错误页面源码的辅助函数"""
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        url_div = soup.new_tag("div", style="font-weight: bold; margin-bottom: 20px;")
        url_div.string = f"Page URL: {url}"
        
        if soup.body:
            soup.body.insert(0, url_div)
        else:
            soup.append(url_div)
            
        # Sanitize filename
        filename_base = re.sub(r'[^a-zA-Z0-9_\-.]', '', url.rsplit('/', 1)[-1] if url else 'error')
        output_folder = "error_pages"
        os.makedirs(output_folder, exist_ok=True)
        
        file_path = os.path.join(output_folder, f'page_source_{filename_base}_{int(time.time())}.html')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(str(soup.prettify())) # Use str() for compatibility with type hints
        print(f"错误页面已保存到 {file_path}")
            
    except Exception as e:
        print(f"保存错误页面失败: {e}") 