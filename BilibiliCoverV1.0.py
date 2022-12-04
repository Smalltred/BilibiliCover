#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2022/12/3 15:22
# @Author  : Small tred
# @FileName: BilibiliCoverV1.0.py
# @Software: PyCharm
# @Blog    ：https://www.hecady.com
import requests
import re
import biliBV
import time


# noinspection PyBroadException
class BilibiliCover:

    def __init__(self, content):
        self.content = content
        self.bv_api = "https://api.bilibili.com/x/web-interface/view?bvid="
        self.ep_api = "https://api.bilibili.com/pgc/view/web/season?ep_id="
        self.ss_api = "https://api.bilibili.com/pgc/view/web/season?season_id="
        self.md_api = "https://api.bilibili.com/pgc/review/user?media_id="
        self.url = "https://www.bilibili.com/"

    def get_video_id(self):
        """匹配文本中的链接 判断链接是否重定向 获取重定向后的链接"""
        try:
            b_url = re.search(r"[a-zA-z]+://[^\s]*", self.content).group(0)
            response = requests.get(b_url)
            if response.status_code == 302:
                real_url = requests.get(b_url, allow_redirects=False).url
                return self.regexId(real_url)
            else:
                return self.regexId(b_url)
        except Exception as e:
            return self.regexId(self.content)

    def regexId(self, string):
        if self.regexBv(string):
            return self.regexBv(string)
        elif self.regexAv(string):
            return self.regexAv(string)
        elif self.regexEp(string):
            return self.regexEp(string)
        elif self.regexSs(self.content):
            return self.regexMd(string)
        else:
            return {"code": 403}

    def regexBv(self, string):
        """匹配BV号"""
        try:
            regex = re.compile(r'(BV.*?).{10}', re.I)
            bv_id = regex.search(string).group(0)
            return bv_id
        except Exception as e:
            return None

    def regexAv(self, string):
        """匹配av号"""
        try:
            regex = re.compile(r"(av.*?)\d+", re.I)
            av_id = regex.search(string).group(0)[2:]
            bv_id = biliBV.encode(av_id)
            return bv_id
        except Exception as e:
            return None

    def regexEp(self, string):
        """匹配ep号"""
        try:
            regex = re.compile(r"(ep.*?)\d+", re.I)
            ep_id = regex.search(string).group(0)[2:]
            return ep_id
        except Exception as e:
            return None

    def regexSs(self, string):
        """匹配SS号"""
        try:
            regex = re.compile(r"(ss.*?)\d+", re.I)
            ss_id = regex.search(string).group(0)[2:]
            return ss_id
        except Exception as e:
            return None

    def regexMd(self, string):
        """匹配Med号"""
        try:
            regex = re.compile(r"(md.*?)\d+")
            md_id = regex.search(string).group(0)[2:]
            return md_id
        except Exception as e:
            return None

    def handleVideoBvResult(self):
        """根据BV号 判断是否有分P 是返回全部分P的信息 否返回该视频的封面"""
        av = "av"
        ls = []
        result = requests.get(self.bv_api + self.get_video_id()).json()
        if result != "n":
            # 多p判断
            if result.get("data").get("ugc_season") is not None:
                for vds in result.get("data").get("ugc_season").get("sections"):
                    for vd in vds.get("episodes"):
                        vd_title = vd.get("title")
                        vd_cover = vd.get("arc").get("pic")
                        vd_bvid = vd.get("bvid")
                        vd_avid = vd.get("aid")
                        data = {
                            "title": vd_title,
                            "image": vd_cover,
                            "bvid": vd_bvid,
                            "avid": av + str(vd_avid),
                            "url": self.url + vd_bvid,
                        }
                        print(data)
                        ls.append(data)
                    return ls
            # 单p判断
            else:
                vd_data = result.get("data")
                vd_title = vd_data.get("title")
                vd_cover = vd_data.get("pic")
                vd_bvid = vd_data.get("bvid")
                vd_avid = vd_data.get("aid")
                data = {
                    "title": vd_title,
                    "image": vd_cover,
                    "bvid": vd_bvid,
                    "avid": av + str(vd_avid),
                    "url": self.url + vd_bvid,
                }
                return data

    def handleSsResult(self):
        av = "av"
        result = self.requestsVideoApi()
        if result.get("result").get("episodes") is not None:
            if result.get("result").get("seasons") is not None:
                for ss in result.get("result").get("seasons"):
                    if ss.get("season_id") == self.get_data():
                        for eps in result.get("result").get("episodes"):
                            if ss.get("new_ep").get("id") == eps.get("id"):
                                ep_title = eps.get("share_copy")
                                ep_cover = eps.get("cover")
                                ep_bvid = eps.get("bvid")
                                ep_avid = eps.get("aid")
                                ep_url = eps.get("share_url")
                                data = {
                                    "title": ep_title,
                                    "image": ep_cover,
                                    "bvid": ep_bvid,
                                    "avid": av + str(ep_avid),
                                    "url": ep_url,
                                    "测试": "1"
                                }
                                return data
        else:
            return "番剧是不是还没上线啊"


def mian():
    a = ""
    av = "av216845"
    d_bv = "https://www.bilibili.com/video/BV1DP4y197WS/?spm_id_from=333.851.b_7265636f6d6d656e64.2"
    s_bv = "https://www.bilibili.com/video/BV1K24y1k7XA/?spm_id_from=333.851.b_7265636f6d6d656e64.3"
    url = "www.hecady.com/ssadasdasd"
    text = "sdfsdasda.sad561as5646"
    bv_id = "BV1QM41167tFadasdadsa"
    wsx_ss = "https://www.bilibili.com/bangumi/play/ss43148?from_spmid=666.14.0.0"
    sx_ss = "https://www.bilibili.com/bangumi/play/ss42652?from_spmid=666.14.0.0"
    ep_id = "https://www.bilibili.com/bangumi/play/ep567775?from_spmid=666.4.banner.3"
    web_md = "https://www.bilibili.com/bangumi/media/md28339205/?spm_id_from=666.25.b_6d656469615f6d6f64756c65.2"
    web_ep = "https://www.bilibili.com/bangumi/play/ep670659?from_spmid=666.19.0.0"
    web_md1 = "https://www.bilibili.com/bangumi/media/md28339205/?spm_id_from=666.25.b_6d656469615f6d6f64756c65.2"
    ss_vide = "https://www.bilibili.com/bangumi/play/ss28324?from_spmid=666.25.series.0&from_outer_spmid=666.14.0.0"

    start = time.time()
    cover = BilibiliCover(bv_id)
    # print(cover.get_video_id())
    print(cover.handleVideoBvResult())
    end = time.time()
    print(end - start)

mian()