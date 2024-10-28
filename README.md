# Google Indexing API URL Submission Script

此脚本用于从指定的 Sitemap 中提取 URL，并将其提交到 Google Indexing API。您可以为每个域名设置提交的 URL 数量限制，以便更好地管理您的网站索引。

## 功能

- 从多个 Sitemap 中提取 URL。
- 将提取的 URL 提交到 Google Indexing API。
- 支持为每个 Sitemap 设置最大提交数量。
- 记录提交结果到日志文件。

## 先决条件

在运行此脚本之前，您需要：

1. **Python 3.x**：确保您的系统上安装了 Python 3.x。
2. **所需库**：安装以下 Python 库：
   ```bash
   pip3 install requests google-auth
   ```

3. **Google API 凭证**：您需要一个 Google Cloud 项目，并启用 Indexing API。创建服务账户并下载 JSON 格式的凭证文件，命名为 `key.json`，并将其放在与脚本相同的目录中。

## 使用方法

1. **配置 Sitemap URL 和最大提交数量**：
   在脚本中，您可以在 `SITEMAP_URLS` 列表中添加您的 Sitemap URL 和对应的最大提交数量。例如：
   ```python
   SITEMAP_URLS = [
       ('https://darklotus.cn/sitemap.xml', 100),  # 第一个 sitemap URL 和最大提交数量
       ('https://blog.darklotus.cn/sitemap.xml', 100),  # 第二个 sitemap URL 和最大提交数量
   ]
   ```

2. **运行脚本**：
   在终端中运行以下命令：
   ```bash
   python3 api.py
   ```

3. **查看日志**：
   提交结果将记录在 `submission_log.txt` 文件中，您可以查看成功和失败的提交情况。

## 代码说明

- **获取凭证**：使用 Google 服务账户凭证进行身份验证。
- **提取 URL**：从指定的 Sitemap 中提取 URL。
- **提交 URL**：将提取的 URL 提交到 Google Indexing API。
- **并发处理**：使用线程池并发提交 URL，提高效率。

## 示例代码

以下是脚本的主要部分：

```python
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
]

# 其他代码...
```

## 许可证

此项目使用 MIT 许可证。有关详细信息，请参阅 [LICENSE](LICENSE) 文件。

## 贡献

欢迎任何形式的贡献！请提交问题或拉取请求。

