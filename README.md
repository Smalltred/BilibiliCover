

# BilibiliCove

自学Python的一个小小的工具！

# 环境

```
Python3.9 基于Flask的轻量级服务
```

# 部署

```
pip install -r requirements.txt
git clone https://github.com/Smalltred/BilibiliCover.git
cd BilibiliCover
python3 manage.py runserver
```

# API

可以使用API进行调用，且**API后的参数不能为空**

```
https://localhost/api?b=https://www.bilibili.com/video/BV19d4y1t7sS/
```

## 返回内容

|  内容  |          说明          |
| :----: | :--------------------: |
| title  |        视频标题        |
| image  |        视频封面        |
|  bvid  |        B站BV号         |
|  url   |      B站视频地址       |
| volume |        番剧集数        |
| states | 番剧上线为1，未上线为2 |

# 错误说明

返回下列内容表示传入参数错误。

```json
{
  "code": "403", 
  "msg": "参数不合法"
}
```


