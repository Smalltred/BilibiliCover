#!/usr/bin/python
# -- coding: utf-8 --
import requests
import os
import re

headers = {
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.164 Safari/537.36",
}

api = "https://api.bilibili.com/x/web-interface/view?bvid="


def handles_url(in_url):
        regex = re.compile(r'(BV.*?)\?')
        return re.search(regex, in_url).group(1)


def requests_url(req_url):
    return requests.get(req_url, headers=headers)


def handles_response():
    result = requests_url(bvurl).json()
    title = result["data"]["title"]
    img_url = result["data"]["pic"]
    print(title, img_url)
    return title, img_url


def createdir():
    if os.path.exists(path):
        download()
    else:
        os.mkdir(path)
        download()


def download():
    with open(os.path.join(path, download_title + ".jpg"), 'wb') as f:
        f.write(requests_url(download_url).content)
        print("下载成功！")


if __name__ == '__main__':
    path = "images"
    url = input("请输入带有Bv号的链接或者分享分享链接支持(手机): \n")
    try:
        bvid = handles_url(url)
        bvurl = api + bvid
        download_title, download_url = handles_response()
        download()
    except:
        print("错误，请检查链接是否正确")


