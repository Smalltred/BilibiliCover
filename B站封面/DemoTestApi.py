import requests

api = "https://v2.alapi.cn/api/bilibili/cover"
data = {
    "c": "",
    "token": "VJF3R1rR5A7PCxyK"

}


def user_input():
    print("请输入视频地址：")
    url = input()
    data["c"] = url


def get_img():
    result = requests.get(api, params=data).json()
    img_url = result["data"]["cover"]
    img_title = result["data"]["title"]
    img = img_title + ", " + img_url
    return img


while True:
    user_input()
    try:
        get_img()
        print("是否要保存到文件内？ 按回车键保存/输入任意键打印")
        if input() == "":
            with open("封面地址.txt", "a", encoding="UTF-8") as f:
                f.write(get_img() + "\n")
                print("保存成功！")
            break
        else:
            print(get_img())
    except TypeError:
        print("\n请输入正确的视频地址！")
