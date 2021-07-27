import requests
import re

header = {
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.164 Safari/537.36",
}

url = "https://www.bilibili.com/video/av86863038"
url2 = "https://www.bilibili.com/video/BV1ng411M7F1?spm_id_from=333.851.b_7265636f6d6d656e64.1"
# 正则匹配BV/av号
a = re.compile("\\w+")
b = a.findall(url)
print(b[5])
#
# api = "https://api.bilibili.com/x/web-interface/view?bvid={}".format()


# response = requests.get(api, headers=header).json()
# print(response)
