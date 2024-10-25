import requests
import xml.etree.ElementTree as ET
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from concurrent.futures import ThreadPoolExecutor

# 设置 User-Agent 头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 参数配置
SITEMAP_URLS = [
    ('https://darklotus.cn/sitemap.xml', 100),  # 第一个 sitemap URL 和最大提交数量
    ('https://blog.darklotus.cn/sitemap.xml', 100),  # 第二个 sitemap URL 和最大提交数量
    # 可以添加更多的 sitemap URL 和对应的最大数量
]
KEY_FILE = 'key.json'  # 假设 key.json 与脚本在同一目录
GOOGLE_INDEXING_API_URL = 'https://indexing.googleapis.com/v3/urlNotifications:publish'

# 获取凭证
def get_credentials():
    try:
        credentials = service_account.Credentials.from_service_account_file(
            KEY_FILE,
            scopes=['https://www.googleapis.com/auth/indexing']
        )
        return credentials
    except Exception as e:
        print(f"Error getting credentials: {e}")
        return None

# 从 sitemap.xml 获取 URL
def get_urls_from_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url, headers=HEADERS)
        response.raise_for_status()  # 检查请求是否成功
        urls = []
        root = ET.fromstring(response.content)
        # 查找所有 loc 标签
        for loc in root.findall('.//{*}loc'):
            urls.append(loc.text)
        return urls
    except Exception as e:
        print(f"Error fetching URLs from sitemap: {e}")
        return []

# 提交 URL 到 Google Indexing API
def submit_url_to_google(url, credentials):
    try:
        headers = {
            'Content-Type': 'application/json',
        }
        body = {
            'url': url,
            'type': 'URL_UPDATED'
        }
        auth_request = Request()
        credentials.refresh(auth_request)
        access_token = credentials.token
        headers['Authorization'] = f'Bearer {access_token}'
        
        response = requests.post(GOOGLE_INDEXING_API_URL, json=body, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        return response.status_code, response.text
    except Exception as e:
        print(f"Error submitting URL {url}: {e}")
        return None, str(e)

# 主程序
def main():
    credentials = get_credentials()
    if credentials is None:
        return  # 如果凭证获取失败，退出程序

    total_success = 0
    total_failure = 0

    # 日志记录
    log_file = 'submission_log.txt'
    with open(log_file, 'w') as log:
        with ThreadPoolExecutor(max_workers=5) as executor:  # 设置并发线程数
            for sitemap_url, max_urls in SITEMAP_URLS:
                urls = get_urls_from_sitemap(sitemap_url)
                if not urls:
                    print(f"No URLs found in sitemap: {sitemap_url}.")
                    continue  # 如果没有找到 URL，跳过当前 sitemap

                # 限制提交的 URL 数量
                urls_to_submit = urls[:max_urls]  # 取前 max_urls 个 URL

                futures = {executor.submit(submit_url_to_google, url, credentials): url for url in urls_to_submit}
                for future in futures:
                    url = futures[future]
                    try:
                        status_code, response_text = future.result()
                        log_entry = f'Submitted {url}: {status_code} - {response_text}\n'
                        print(log_entry.strip())  # 打印到控制台
                        log.write(log_entry)  # 写入日志文件
                        total_success += 1  # 成功计数
                    except Exception as e:
                        log_entry = f'Failed to submit {url}: {e}\n'
                        print(log_entry.strip())  # 打印错误信息
                        log.write(log_entry)  # 写入日志文件
                        total_failure += 1  # 失败计数

    # 打印总结
    print(f"\nTotal URLs submitted successfully: {total_success}")
    print(f"Total URLs failed to submit: {total_failure}")

if __name__ == '__main__':
    main()
