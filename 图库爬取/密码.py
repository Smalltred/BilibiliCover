
name = open("password.txt", "r", encoding="utf-8")
account = name.readlines()

user = []
pwd = []
try:
    for a in account:
        account_list = a.split('----', 1)
        user.append(account_list[0])
        pwd.append(account_list[1])
except IndexError:
    print("请检查导入的账号密码格式！")

if len(user) == len(pwd):
    qty = len(user)
    print("一共{}个账号！".format(qty))

else:
    print("账号密码数量不匹配！")
