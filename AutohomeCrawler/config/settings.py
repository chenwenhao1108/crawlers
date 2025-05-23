# settings.py

# WebDriver settings
# CHROME_DRIVER_PATH = 'crawler/chromedriver-win64/chromedriver.exe' # Uncomment and specify if using a local chromedriver
CHROME_DRIVER_URL = "https://registry.npmmirror.com/-/binary/chromedriver" # Or use webdriver-manager
COOKIES_FILE = "data/autohome_cookies.pkl"
USER_PROFILE_URL = 'https://i.autohome.com.cn/' # AutoHome User Profile URL (replace with a valid one if needed)
BASE_URL = "https://club.autohome.com.cn"

# Data files
POSTS_FILE = "data/autohome_posts.json"
PROGRESS_FILE = "data/autohome_progress.json"

# Community settings
# Define communities to scrape in the format: {'community_name': {'url_template': 'url_with_{page_num}', 'total_pages': N, 'page_offset': M}}
COMMUNITIES = {
    # Example:
    'lixiang_l6': {
        'url_template': 'https://club.autohome.com.cn/bbs/forum-c-6950-{page_num}.html#pvareaid=3454448',
        'total_pages': 1,
        'page_offset': 0
    },
    # Add other communities here, e.g.:
    # 'another_car': {
    #     'url_template': 'https://club.autohome.com.cn/bbs/forum-c-xxxx-{page_num}.html',
    #     'total_pages': 20,
    #     'page_offset': 0
    # }
}

# Selenium settings
WAIT_TIME = 10
SCROLL_WAIT_TIME = 1
RANDOM_DELAY_RANGE = (1, 3) # seconds

# Chrome options (adjust as needed)
CHROME_OPTIONS = [
    '--disable-plugins-discovery',
    '--mute-audio',
    #'--headless', # Uncomment for headless mode
    "--disable-gpu",
    "--no-sandbox", # Required for some environments
    "--disable-dev-shm-usage", # Required for some environments
    "--disable-blink-features=AutomationControlled",
    "--disable-extensions", # Disable extensions
    "--disable-software-rasterizer", # Disable software rasterizer
    "--disable-webgl", # Disable WebGL
    "--log-level=3", # Suppress most messages
    "--silent-debugger-extension-api", # Suppress debugger API logs
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 Edg/89.0.774.77", # Example User-Agent
]

# Preferences
CHROME_PREFS = {
    # "profile.managed_default_content_settings.images": 2 # Disable images
} 