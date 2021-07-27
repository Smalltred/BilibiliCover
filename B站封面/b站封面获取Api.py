import requests


class Main:

    @staticmethod
    def response():
        response = requests.get(api, params=data).json()
        return response

    @staticmethod
    def get_img_url():
        response = run.response()
        img_url = response["data"]["cover"]
        return img_url
    @staticmethod
    def get_img_title():
        pass


api = "https://v2.alapi.cn/api/bilibili/cover"
print("请输入视频链接!")
url = input()
data = {
    "c": url,
    "token": "VJF3R1rR5A7PCxyK",
}
run = Main()
run.response()
# run.get_img_url()
with open("封面地址.txt", "a", encoding="UTF-8") as f:
    f.write(run.get_img_url() + "\n")
