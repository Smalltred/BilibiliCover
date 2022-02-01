import requests
import re

header = {
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.164 Safari/537.36",
}

api = "https://api.bilibili.com/x/web-interface/view?bvid="

print("请输入带有BV的视频链接！")
url = input()

regex = re.compile("\\w+")
result = regex.findall(url)
bvid = result[5]

response = requests.get(api + bvid, headers=header).json()
img_title = response["data"]["title"]
img_url = response["data"]["pic"]
img = img_title + ", " + img_url

print("是否要保存到文件内？ 按回车键保存/输入任意键打印")
if input() == "":
    with open("封面地址.txt", "a", encoding="UTF-8") as f:
        f.write(img + "\n")
    print("保存成功！")
else:
    print(img)
