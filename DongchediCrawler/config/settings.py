# settings.py

# WebDriver settings
CHROME_DRIVER_URL = "https://registry.npmmirror.com/-/binary/chromedriver"
COOKIES_FILE = "data/dongchedi_cookies.pkl"
USER_PROFILE_URL = "https://www.dongchedi.com/"
BASE_URL = "https://www.dongchedi.com"

# Data files
POSTS_FILE = "data/dongchedi_posts.json"
PROGRESS_FILE = "data/progress.json"

# Community settings
# Define communities to scrape in the format: {'community_name': {'url': 'community_url', 'total_pages': N, 'page_offset': M}}
COMMUNITIES = {
    'lixiang_l8': {
        'url': 'https://www.dongchedi.com/community/6095',
        'total_pages': 1,
        'page_offset': 0
    },
    # Add other communities here, e.g.:
    # 'another_community': {
    #     'url': 'https://www.dongchedi.com/community/xxxx',
    #     'total_pages': 50,
    #     'page_offset': 0
    # }
}

# Selenium settings
WAIT_TIME = 10
SCROLL_WAIT_TIME = 2
RANDOM_DELAY_RANGE = (1, 3) # seconds

# Chrome options (adjust as needed)
CHROME_OPTIONS = [
    '--disable-plugins-discovery',
    '--mute-audio',
    #'--headless', # Uncomment for headless mode
    "--disable-experimental-report-ad-attribution",
    "--disable-blink-features=AutomationControlled",
    "--disable-infobars",
    "--disable-gpu",
    "--no-sandbox", # Required for some environments
    "--disable-dev-shm-usage", # Required for some environments
    "--log-level=3", # Suppress most messages
    "--silent-debugger-extension-api", # Suppress debugger API logs
    "--disable-webgl", # Disable WebGL
    "--disable-software-rasterizer", # Disable software rasterizer
    "--disable-extensions", # Disable extensions
]

# Preferences
CHROME_PREFS = {
    "profile.managed_default_content_settings.images": 2 # Disable images
} 