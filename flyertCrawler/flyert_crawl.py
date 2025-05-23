from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json
import time

from utils import *
from webdriver_manager.chrome import ChromeDriverManager


# 创建 Chrome 选项对象
chrome_options = Options()

chrome_options.add_argument('--disable-plugins-discovery')
chrome_options.add_argument('--mute-audio')
# 开启无头模式，禁用视频、音频、图片加载，开启无痕模式，减少内存占用
# chrome_options.add_argument('--headless')   # 开启无头模式以节省内存占用，较低版本的浏览器可能不支持这一功能
chrome_options.add_argument("--disable-plugins-discovery")
chrome_options.add_argument("--mute-audio")
chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
chrome_options.add_argument("--incognito")
# 禁用GPU加速，避免浏览器崩溃
chrome_options.add_argument("--disable-gpu")



def get_article_links_by_page(hotel, search_result_link, driver, startTime = datetime.strptime('2024-3-1', "%Y-%m-%d"), endTime = datetime.strptime('2025-2-28', "%Y-%m-%d"), time_out=10):
    """从搜索结果页中获取指定时间范围内的每篇文章的链接，并且获取一页的链接就直接写入json文件

    Args:
        hotel (str): 酒店名
        search_result_link (str): 搜索结果页的链接
        driver: webdriver
        startTime (datetime, optional): _description_. Defaults to datetime.strptime('2024-3-1', "%Y-%m-%d").
        endTime (datetime, optional): _description_. Defaults to datetime.strptime('2025-2-28', "%Y-%m-%d").
        time_out (int, optional): 等待时间，Defaults to 10.

    Returns:
        list: 该搜索结果下的所有文章链接
    """
    try:
        wait = WebDriverWait(driver, time_out)

        more = True
        page_num = 1
        links = []

        # 获取所有分页下的文章链接
        while more:
            print(f'Scraping page {page_num} of {hotel}')
            page_url = f"{search_result_link}&page={page_num}"
            driver.get(page_url)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".tl")))
            scroll_to_bottom(driver)
            
            try:
                empty_elements = driver.find_elements(By.CSS_SELECTOR, "p.emp")
                if empty_elements and any("抱歉" in elem.text for elem in empty_elements):
                    print(f"已到达最后一页或没有更多内容，hotel: {hotel}")
                    more = False
                    break
            except:
                pass
            
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.pbw p:nth-of-type(3) span:first-of-type")))
            searchResults = driver.find_elements(By.CSS_SELECTOR, "li.pbw")
            print(f"当前页面文章数量: {len(searchResults)}")
            
            for result in searchResults:
                try:
                    timestampElem = result.find_element(By.CSS_SELECTOR, "p:nth-of-type(3) span:first-of-type")
                    timeStr = parse_timestamp(timestampElem.text)
                except:
                    try:
                        timestampElem = result.find_element(By.XPATH, ".//h3[@class='search_title']/following-sibling::*[last()]/descendant::span[1]")
                        timeStr = parse_timestamp(timestampElem.text)
                    except:
                        timeStr = None
                if timeStr is None:
                    print(f"获取时间戳失败：{result.get_attribute('outerHTML')}, link: {page_url}")
                    continue
                currentTimestamp = datetime.strptime(timeStr, "%Y-%m-%d %H:%M")

                if currentTimestamp > endTime:
                    print(f"当前时间戳大于截止时间, link: {page_url}")
                    continue
                
                if currentTimestamp < startTime:
                    print(f"当前时间戳小于开始时间, link: {page_url}")
                    more = False
                    break
                
                linkElem = result.find_element(By.CSS_SELECTOR, "h3.search_title a")
                href = linkElem.get_attribute("href")
                if href is not None:
                    links.append(href)
            
            page_num += 1
            
        with open('data/links.json', 'r', encoding='utf-8') as f:
            existing_links = json.load(f)
            
        for existing_hotel in existing_links:
            if existing_hotel['hotel'] == hotel:
                unique_links = [link for link in links if link not in existing_hotel['links']]
                print(f"新增链接数量: {len(unique_links)}")
                existing_hotel['links'].extend(unique_links)
                with open('data/links.json', 'w', encoding='utf-8') as f:
                    json.dump(existing_links, f, ensure_ascii=False, indent=4)
                break
        return links
            
            
    except Exception as e:
        print(f'Failed to get posts from page {page_url}:\n{e}')


def get_all_links(driver):
    """
    调用get_article_links_by_page函数获取所有文章链接
    """
    hotels = [
        # '惠庭',
        # '凯悦嘉轩',
        # '凯悦嘉寓',
        # '馨乐庭',
        # '源宿',
        # '诺富特',
        # '智选假日',
        # '万枫',
        # '美居',
        # '亚朵酒店',
        # '桔子水晶',
        # '城际',
        # '维也纳国际',
        # '丽枫',
        # '途家盛捷',
        # '亚朵轻居'
    ]
    
    search_result_links = [
        # 'https://www.flyert.com.cn/search.php?mod=forum&adv=&srchuname=&searchid=6168&srchtype=title&attach=&srchfid=&before=0&srchfrom=0&srchfilter=all&src_sp=&searchsubmit=yes&kw=Home2&orderby=dateline&ascdesc=desc',
        # 'https://www.flyert.com.cn/search.php?mod=forum&adv=&srchuname=&searchid=6207&srchtype=fulltext&attach=&srchfid=&before=0&srchfrom=0&srchfilter=all&src_sp=&searchsubmit=yes&kw=Hyatt+Place&orderby=dateline&ascdesc=desc',
        # 'https://www.flyert.com.cn/search.php?mod=forum&adv=&srchuname=&searchid=6233&srchtype=fulltext&attach=&srchfid=&before=0&srchfrom=0&srchfilter=all&src_sp=&searchsubmit=yes&kw=Hyatt+House&orderby=dateline&ascdesc=desc',
        # 'https://www.flyert.com.cn/search.php?mod=forum&adv=&srchuname=&searchid=6299&srchtype=fulltext&attach=&srchfid=&before=0&srchfrom=0&srchfilter=all&src_sp=&searchsubmit=yes&kw=Element&orderby=dateline&ascdesc=desc'
        # 'https://www.flyert.com.cn/search.php?mod=forum&adv=&srchuname=&searchid=6333&srchtype=fulltext&attach=&srchfid=&before=0&srchfrom=0&srchfilter=all&src_sp=&searchsubmit=yes&kw=Novotel&orderby=dateline&ascdesc=desc',
        # 'https://www.flyert.com.cn/search.php?mod=forum&adv=&srchuname=&searchid=6356&srchtype=fulltext&attach=&srchfid=&before=0&srchfrom=0&srchfilter=all&src_sp=&searchsubmit=yes&kw=Holiday+Inn+Express&orderby=dateline&ascdesc=desc',
        'https://www.flyert.com.cn/search.php?mod=forum&adv=&srchuname=&searchid=6375&srchtype=fulltext&attach=&srchfid=&before=0&srchfrom=0&srchfilter=all&src_sp=&searchsubmit=yes&kw=Fairfield+Inn&orderby=dateline&ascdesc=desc',
    ]

    for hotel, search_result_link in zip(hotels, search_result_links):
        print(f"正在处理酒店：{hotel}")
        print(f"链接：{search_result_link}")
        get_article_links_by_page(hotel, search_result_link, driver)
    driver.quit()


def get_page_content(url, driver, progress_mgr, time_out=6):
    """获取指定文章的内容及其回复内容
    返回：
        {
            'title': title,
            'timestamp': timestamp,
            'content': content,
            'author': {
                'name': author_name,
                'link': author_href
            },
            'replies': replies
        }
        或者None
    """
    
    try:
        driver.get(url)
        # 快速检测是否存在跳转提示
        short_wait = WebDriverWait(driver, 3)
        try:
            jump_elem = short_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#ShowDiv")))
            if '自动跳转' in jump_elem.text:
                print("检测到跳转提示，跳过当前链接")
                progress_mgr.mark_empty_link(url)
                return None
            else:
                print("检测到跳转元素，但未找到跳转提示，继续处理")
                print(f"跳转元素内容：{jump_elem.text}")
        except:
            pass
        
        wait = WebDriverWait(driver, time_out)
        title_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#thread_subject")))
        timestamp_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[id^='authorposton']")))
        content_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".firstpost")))
        author_link = wait.until(EC.presence_of_element_located((By.XPATH, "//span[starts-with(@id, 'comiis_authi_author_div')]//a[@class='kmxi2']")))
        
        scroll_to_bottom(driver)
        
        # 获取各元素的文本内容
        title = title_elem.text
        timestamp = parse_timestamp(timestamp_elem.text)
        content = content_elem.text
        author_name = author_link.text
        author_href = author_link.get_attribute('href')

        # 遍历每个回复容器，找到作者链接和回复内容
        more_pages = True
        first_page = True
        replies = []
        while more_pages:
            if first_page:
                reply_containers = driver.find_elements(By.CSS_SELECTOR, ".comiis_viewbox")[1:]
            else:
                reply_containers = driver.find_elements(By.CSS_SELECTOR, ".comiis_viewbox")
                
            for container in reply_containers:
                commenter_name = ''
                comment_content = ''
                commenter_link = ''
                comment_time = ''
                
                possible_links = container.find_elements(By.CSS_SELECTOR, ".authi.l>a")
                for link in possible_links:
                    href = link.get_attribute("href")
                    if href and ('home.php?mod=space&uid=' in href):
                        commenter_name = link.text
                        commenter_link = link.get_attribute('href')
                        break
                    
                content_element = container.find_element(By.CSS_SELECTOR, ".post_message")
                if content_element:
                    comment_content = content_element.text
                    
                comment_time_element = container.find_element(By.CSS_SELECTOR, "[id^='authorposton']")
                if comment_time_element:
                    comment_time = parse_timestamp(comment_time_element.text)
                replies.append({
                    'commenter_name': commenter_name,
                    'comment_content': comment_content,
                    'commenter_link': commenter_link,
                    'comment_time': comment_time
                })
                
            # 处理完当前页所有评论后再查找下一页按钮
            possible_next_page_button = driver.find_elements(By.CSS_SELECTOR, ".nxt")
            
            for button in possible_next_page_button:
                if 'page' in button.get_attribute("href"):
                    # 使用 JavaScript 滚动到按钮位置
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(1)  # 等待滚动完成
                    # 使用 JavaScript 点击按钮
                    driver.execute_script("arguments[0].click();", button)
                    first_page = False
                    time.sleep(3)
                    break
            else:
                more_pages = False
        
        # 返回所有获取的内容
        return {
            'title': title,
            'timestamp': timestamp,
            'content': content,
            'author': {
                'name': author_name,
                'link': author_href
            },
            'replies': replies
        }
        
    except Exception as e:
        print(f"Failed to find elements for {url}\n{e}")
        progress_mgr.mark_error_link(url)
        return None
    

def get_all_contents(driver):
    """根据获取到的文章链接调用get_page_content函数获取文章内容
    并将获取到的内容写入json文件
    """
    # 初始化进度管理器
    progress_mgr = ProgressManager()
    
    results_count = {}
    
    # 读取链接数据
    with open(f'data/links.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 读取或创建结果文件
    try:
        with open(f'data/flyert-1.json', 'r', encoding='utf-8') as f:
            new_data = json.load(f)
    except:
        new_data = []
    
    # 从上次的进度继续处理
    start_from_hotel = False
    if progress_mgr.get_current_hotel() == "":
        start_from_hotel = True
        
    for item in data:
        hotel = item['hotel']
        
        if hotel not in results_count:
            results_count[hotel] = 0
        
        # 如果还没到上次处理的酒店，就跳过
        if not start_from_hotel and hotel != progress_mgr.get_current_hotel():
            continue
        start_from_hotel = True
        
        # 更新当前处理的酒店
        progress_mgr.set_current_hotel(hotel)
        
        # 检查是否需要创建新的酒店数据
        if not any(i['hotel'] == hotel for i in new_data):
            new_data.append({
                'hotel': hotel,
                'posts': []
            })
        
        # 处理每个链接
        for link in item['links']:
            # 跳过已处理的链接
            if progress_mgr.is_link_processed(link):
                continue
                
            try:
                result = get_page_content(link, driver, progress_mgr)
                if result:
                    result['link'] = link
                    # 更新数据
                    for tmp in new_data:
                        if tmp['hotel'] == hotel:
                            tmp['posts'].append(result)
                            break
                    
                    # 保存结果
                    with open(f'data/flyert-1.json', 'w', encoding='utf-8') as f:
                        json.dump(new_data, f, ensure_ascii=False, indent=4)
                    
                    # 标记链接为已处理
                    progress_mgr.mark_link_processed(link)
                    results_count[hotel] += 1
                    
                time.sleep(5)  # 请求间隔
                
            except Exception as e:
                print(f"Error processing {link}: {str(e)}")
                continue
        
        # 完成当前酒店的处理
        progress_mgr.set_current_hotel("")
    
    for hotel, count in results_count.items():
        print(f"酒店 {hotel} 新增数据： {count}")


def main():
    test_cookies()
    
    start_time = time.perf_counter()
    
    service = Service(ChromeDriverManager(url="https://registry.npmmirror.com/-/binary/chromedriver").install())
    driver = webdriver.Chrome(service=service, options=chrome_options) 

    driver.get('https://www.flyert.com.cn/')
    load_cookies(driver, cookies_file)

    wait = WebDriverWait(driver, 30)
    # 等待页面基本元素加载完成
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    driver.set_window_size(1920, 1080)
    
    # 先执行get_all_links函数获取所有文章链接，再执行get_all_contents函数获取文章内容
    # get_all_links(driver)
    get_all_contents(driver)


    driver.quit()
        
    end_time = time.perf_counter()
    print(f'Total time cost: {round(end_time - start_time)} seconds')

if __name__ == "__main__":
    main()
