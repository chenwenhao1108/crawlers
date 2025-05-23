# utils.py

import json
import os
import pickle
import time
import random
from datetime import datetime, timedelta
import re


def parse_time_string(time_str):
    # 去除结尾的“回复”
    time_str = time_str.strip().rstrip("回复").strip()

    now = datetime.now()

    # 匹配 "刚刚"
    if time_str == "刚刚":
        return int((now - timedelta(minutes=1)).timestamp())

    # 匹配 x分钟前
    minute_match = re.search(r'(\d+)分钟前', time_str)
    if minute_match:
        minutes_ago = int(minute_match.group(1))
        return int((now - timedelta(minutes=minutes_ago)).timestamp())

    # 匹配 x小时前
    hour_match = re.search(r'(\d+)小时前', time_str)
    if hour_match:
        hours_ago = int(hour_match.group(1))
        return int((now - timedelta(hours=hours_ago)).timestamp())

    # 匹配 昨天 hh:mm
    yesterday_match = re.search(r'昨天 (\d{2}:\d{2})', time_str)
    if yesterday_match:
        hour, minute = map(int, yesterday_match.group(1).split(':'))
        yesterday = (now - timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        return int(yesterday.timestamp())

    # 匹配 前天 hh:mm
    day_before_yesterday_match = re.search(r'前天 (\d{2}:\d{2})', time_str)
    if day_before_yesterday_match:
        hour, minute = map(int, day_before_yesterday_match.group(1).split(':'))
        day_before = (now - timedelta(days=2)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        return int(day_before.timestamp())

    # 匹配 x天前
    day_match = re.search(r'(\d+)天前', time_str)
    if day_match:
        days_ago = int(day_match.group(1))
        return int((now - timedelta(days=days_ago)).timestamp())

    # 匹配 mm-dd
    md_match = re.search(r'(\d{2})-(\d{2})', time_str)
    if md_match:
        month, day = map(int, md_match.groups())
        try:
            dt = now.replace(month=month, day=day, hour=0, minute=0, second=0, microsecond=0)
            # 如果日期比现在还大（比如12月解析成当前年份的1月），则自动减一年
            if dt > now:
                dt = dt.replace(year=dt.year - 1)
            return int(dt.timestamp())
        except ValueError:
            pass  # 比如 02-30 是非法日期

    # 匹配 yyyy-mm-dd
    ymd_match = re.search(r'(\d{4}-\d{2}-\d{2})', time_str)
    if ymd_match:
        try:
            dt = datetime.strptime(ymd_match.group(1), "%Y-%m-%d")
            return int(dt.timestamp())
        except ValueError:
            pass

    # 匹配 yyyy-mm-dd HH:MM:SS
    ymdhms_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', time_str)
    if ymdhms_match:
        try:
            dt = datetime.strptime(ymdhms_match.group(1), "%Y-%m-%d %H:%M:%S")
            return int(dt.timestamp())
        except ValueError:
            pass

    # 都不匹配就返回原字符串
    return time_str


def save_cookies(driver, cookies_file):
    with open(cookies_file, 'wb') as f:
        pickle.dump(driver.get_cookies(), f)


def load_cookies(driver, cookies_file):
    if os.path.exists(cookies_file):
        with open(cookies_file, 'rb') as f:
            cookies = pickle.load(f)
        for cookie in cookies:
            # Check if domain is valid before adding cookie
            if 'domain' in cookie and cookie['domain']:
                driver.add_cookie(cookie)
        return True
    return False


def manual_login(driver, cookies_file, user_profile_url):
    driver.get(user_profile_url)
    input("请登录，登录成功跳转后，按回车键继续...")
    save_cookies(driver, cookies_file)  # 登录后保存cookie到本地
    print("程序正在继续运行")


def scroll_to_bottom(driver, wait_time=2):
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


def load_progress(progress_file):
    """加载爬取进度"""
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_progress(progress_file, progress_data):
    """保存爬取进度"""
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=4) 