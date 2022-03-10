#!/usr/bin/python
# -- coding: utf-8 --
# @Author : Small_tred 
# @Time : 2022/3/10 16:40
import requests
import os
import re

headers = {
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.164 Safari/537.36",
}


api = "https://api.bilibili.com/x/web-interface/view?bvid="

print("请输入带有BV的视频链接！")
url = input()

try:
    regex = re.compile(r'(BV.*?)\?')
    bvid = re.search(regex, url).group(1)
    response = requests.get(api + bvid, headers=headers).json()
    name = response["data"]["bvid"]
    url = response["data"]["pic"]
    download = requests.get(url, headers=headers).content
    if os.path.exists("images"):
        with open(os.path.join("images", name + ".jpg"), "wb") as f:
            f.write(download)
            print("下载完成")
    else:
        os.mkdir("images")
        with open(os.path.join("images", name + ".jpg"), "wb") as f:
            f.write(download)
            print("下载完成")

except Warning:
    print("请输入正确的连接")
