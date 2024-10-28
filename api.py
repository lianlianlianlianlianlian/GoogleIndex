import os
import requests
import xml.etree.ElementTree as ET
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from concurrent.futures import ThreadPoolExecutor

# 参数配置
SITEMAP_URLS = [
    ('https://darklotus.cn/sitemap.xml', 100),  # 第一个 sitemap URL 和最大提交数量
    ('https://blog.darklotus.cn/sitemap.xml', 100),  # 第二个 sitemap URL 和最大提交数量
]
KEY_FILE = 'key.json'  # 假设 key.json 与脚本在同一目录
GOOGLE_INDEXING_API_URL = 'https://indexing.googleapis.com/v3/urlNotifications:publish'  # Google Indexing API URL
MAX_WORKERS = 20  # 设置并发线程数

# 设置 User-Agent 头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 获取凭证
def get_credentials():
    """
    从 key.json 文件获取 Google API 的凭证
    """
    try:
        credentials = service_account.Credentials.from_service_account_file(
            KEY_FILE,
            scopes=['https://www.googleapis.com/auth/indexing']  # 设置访问范围
        )
        return credentials
    except Exception as e:
        print(f"获取凭证时出错: {e}")
        return None

# 从 sitemap.xml 获取 URL
def get_urls_from_sitemap(sitemap_url):
    """
    从指定的 sitemap URL 获取所有的 URL
    """
    try:
        response = requests.get(sitemap_url, headers=HEADERS)  # 发送 GET 请求
        response.raise_for_status()  # 检查请求是否成功
        urls = []
        root = ET.fromstring(response.content)  # 解析 XML 内容
        # 查找所有 loc 标签
        for loc in root.findall('.//{*}loc'):
            urls.append(loc.text)  # 将 URL 添加到列表中
        return urls
    except Exception as e:
        print(f"从 sitemap 获取 URL 时出错: {e}")
        return []

# 提交 URL 到 Google Indexing API
def submit_url_to_google(url, credentials):
    """
    将指定的 URL 提交到 Google Indexing API
    """
    try:
        headers = {
            'Content-Type': 'application/json',  # 设置请求内容类型为 JSON
        }
        body = {
            'url': url,  # 提交的 URL
            'type': 'URL_UPDATED'  # URL 类型
        }
        auth_request = Request()
        credentials.refresh(auth_request)  # 刷新凭证
        access_token = credentials.token  # 获取访问令牌
        headers['Authorization'] = f'Bearer {access_token}'  # 设置授权头
        
        response = requests.post(GOOGLE_INDEXING_API_URL, json=body, headers=headers)  # 发送 POST 请求
        response.raise_for_status()  # 检查请求是否成功
        return response.status_code, response.text  # 返回状态码和响应文本
    except Exception as e:
        print(f"提交 URL {url} 时出错: {e}")
        return None, str(e)

# 主程序
def main():
    """
    主程序，执行获取 URL 和提交 URL 的过程
    """
    credentials = get_credentials()  # 获取凭证
    if credentials is None:
        return  # 如果凭证获取失败，退出程序

    total_success = 0  # 成功计数
    total_failure = 0  # 失败计数

    # 日志记录
    log_file = 'submission_log.txt'
    with open(log_file, 'w') as log:  # 打开日志文件
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:  # 设置并发线程数
            for sitemap_url, max_urls in SITEMAP_URLS:  # 遍历每个 sitemap URL
                urls = get_urls_from_sitemap(sitemap_url)  # 获取 URL 列表
                if not urls:
                    print(f"在 sitemap 中未找到 URL: {sitemap_url}.")
                    continue  # 如果没有找到 URL，跳过当前 sitemap

                # 限制提交的 URL 数量
                urls_to_submit = urls[:max_urls]  # 取前 max_urls 个 URL

                # 提交 URL 的并发操作
                futures = {executor.submit(submit_url_to_google, url, credentials): url for url in urls_to_submit}
                for future in futures:  # 遍历每个未来对象
                    url = futures[future]  # 获取对应的 URL
                    try:
                        status_code, response_text = future.result()  # 获取结果
                        log_entry = f'提交 {url}: {status_code} - {response_text}\n'  # 日志条目
                        print(log_entry.strip())  # 打印到控制台
                        log.write(log_entry)  # 写入日志文件
                        total_success += 1  # 成功计数
                    except Exception as e:
                        log_entry = f'提交 {url} 失败: {e}\n'  # 错误日志
                        print(log_entry.strip())  # 打印错误信息
                        log.write(log_entry)  # 写入日志文件
                        total_failure += 1  # 失败计数

    # 打印总结
    print(f"\n成功提交的 URL 总数: {total_success}")
    print(f"提交失败的 URL 总数: {total_failure}")

if __name__ == '__main__':
    main()