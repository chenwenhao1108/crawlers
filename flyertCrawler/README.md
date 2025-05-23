## 使用方法

1.  **安装依赖:**

    ```bash
    cd flyertCrawler
    ```

    ```bash
    pip install -r requirements.txt
    ```

2.  **运行爬虫:**

    ```bash
    python flyert_crawl.py
    ```

    首次运行时，程序会提示您登录飞客茶馆网站。登录成功后，会将 Cookies 保存到 `cookies.pkl` 文件中，后续运行将自动加载 Cookies。

3.  **查看结果:**

    *   抓取的帖子链接会保存在 `data/links.json`。
    *   抓取的帖子详细内容会保存在 `data/flyert.json`。
    *   爬虫的运行进度会记录在 `data/progress.json`。