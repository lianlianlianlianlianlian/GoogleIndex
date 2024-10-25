from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import json

SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

# service_account_file.json is the private key that you created for your service account.
JSON_KEY_FILE = "key.json"

# 获取凭证
try:
    credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=SCOPES)
except Exception as e:
    print("Error loading credentials:", e)
    exit(1)

# 授权 HTTP 客户端
http = credentials.authorize(httplib2.Http())

# 定义要提交的内容
content = {
    "url": "http://darklotus.cn",  # 替换为您要提交的 URL
    "type": "URL_UPDATED"
}

# 将内容转换为 JSON 字符串
content_json = json.dumps(content)

# 发送请求
try:
    response, content = http.request(ENDPOINT, method="POST", body=content_json)
    # 打印响应
    print("Response status:", response.status)
    print("Response content:", content.decode('utf-8'))  # 解码为字符串
except Exception as e:
    print("Error during request:", e)
