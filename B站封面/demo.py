import requests
import json

api_url = "https://v2.alapi.cn/api/bilibili/cover"
vd_url = "https://www.bilibili.com/video/av86863038"
data = {
    "c": vd_url,
    "token": "VJF3R1rR5A7PCxyK",
}
response = requests.get(api_url, params=data).json()

# data = response["data"]["cover"]

print(data)
print(response)