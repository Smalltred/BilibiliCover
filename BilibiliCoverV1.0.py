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
        self.md_all_api = "https://api.bilibili.com/pgc/web/season/section?season_id="
        self.url = "https://www.bilibili.com/"
        self.av = "av"

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
        bv_id = self.regexBv(string)
        av_id = self.regexAv(string)
        ep_id = self.regexEp(string)
        ss_id = self.regexSs(string)
        md_id = self.regexMd(string)
        if bv_id:
            return bv_id
        elif av_id:
            return av_id
        elif ep_id:
            return ep_id
        elif ss_id:
            return ss_id
        elif md_id:
            return md_id
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
        except Exception:
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

    def handleBvResult(self):
        """根据BV号 判断是否有分P 是返回全部分P的信息 否返回该视频的封面"""
        data = []
        bv_id = self.get_video_id()
        result = requests.get(self.bv_api + bv_id).json()
        # 多p判断
        if result.get("data").get("ugc_season") is not None:
            for vds in result.get("data").get("ugc_season").get("sections"):
                for vd in vds.get("episodes"):
                    vd_title = vd.get("title")
                    vd_cover = vd.get("arc").get("pic")
                    vd_bvid = vd.get("bvid")
                    vd_avid = self.av + str(vd.get("aid"))
                    temp = {
                        "title": vd_title,
                        "image": vd_cover,
                        "bvid": vd_bvid,
                        "avid": vd_avid,
                        "url": self.url + vd_bvid,
                    }
                    print(temp)
                    data.append(temp)
                return data
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
                "avid": self.av + str(vd_avid),
                "url": self.url + vd_bvid,
            }
            return data

    def handleEpResult(self):

        """
        1.判断请求内容是否存在
        2.判断番剧是否上线  是 继续判断是(pv或小剧场)还是番剧 否 判断是否为(pv或小剧场)"""

        ep_id = self.get_video_id()
        result = requests.get(self.ep_api + ep_id).json()
        # 判断番剧是否上线 0 没上线 1 上线
        if len(result.get("result").get("episodes")) != 0:
            for eps in result.get("result").get("episodes"):
                # 判断是番剧封面还是PV封面
                if eps.get("id") == int(ep_id):
                    ep_title = eps.get("share_copy")
                    ep_cover = eps.get("cover")
                    ep_bvid = eps.get("bvid")
                    ep_avid = eps.get("aid")
                    ep_url = eps.get("share_url")
                    data = {
                        "title": ep_title,
                        "image": ep_cover,
                        "bvid": ep_bvid,
                        "avid": self.av + str(ep_avid),
                        "url": ep_url,
                    }
                    return data
        # 判断是番剧封面还是PV封面
        else:
            for pvs in result.get("result").get("section"):
                for pv in (pvs.get("episodes")):
                    if pv.get("id") == int(ep_id):
                        ep_pv_title = pv.get("share_copy")
                        ep_pv_cover = pv.get("cover")
                        ep_pv_bvid = pv.get("bvid")
                        ep_pv_avid = pv.get("aid")
                        ep_pv_url = pv.get("share_url")
                        data = {
                            "title": ep_pv_title,
                            "image": ep_pv_cover,
                            "bvid": ep_pv_bvid,
                            "avid": self.av + str(ep_pv_avid),
                            "url": ep_pv_url,
                        }
                        return data

    def handleSsResult(self):
        ss_id = self.get_video_id()
        result = requests.get(self.ss_api + ss_id).json()
        # 上线了则
        if len(result.get("result").get("episodes")) != 0:
            if result.get("result").get("seasons") is not None:
                for ss in result.get("result").get("seasons"):
                    if ss.get("season_id") == int(ss_id):
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
                                    "avid": self.av + str(ep_avid),
                                    "url": ep_url,
                                    "测试": "1"
                                }
                                return data
        # 没上线则
        else:
            if len(result.get("result").get("section")) != 0:
                for pvs in result.get("result").get("section"):
                    for pv in (pvs.get("episodes")):
                        ep_title = pv.get("share_copy")
                        ep_cover = pv.get("cover")
                        ep_bvid = pv.get("bvid")
                        ep_avid = pv.get("aid")
                        ep_url = pv.get("share_url")
                        data = {
                            "title": ep_title,
                            "image": ep_cover,
                            "bvid": ep_bvid,
                            "avid": self.av + str(ep_avid),
                            "url": ep_url,
                        }
                        return data

    def handleMdResult(self):
        ep_ls = []
        ep_pv_ls = []
        md_id = self.get_video_id()
        result = requests.get(self.md_api + md_id).json()
        ssid = result.get("result").get("media").get("season_id")
        title = result.get("result").get("media").get("title")
        md_cover = result.get("result").get("media").get("cover")
        md_url = result.get("result").get("media").get("share_url")
        eps_data = requests.get(self.md_all_api + str(ssid)).json()
        if eps_data.get("result").get("main_section") is not None:
            episodes_data = eps_data.get("result").get("main_section").get("episodes")
            episodes_pv_data = eps_data.get("result").get("section")
            if len(episodes_pv_data) != 0:
                for eps_pv_data in episodes_pv_data:
                    for ep_pv_data in eps_pv_data.get("episodes"):
                        ep_pv_title = ep_pv_data.get("long_title")
                        if ep_pv_title == "":
                            ep_pv_title = ep_pv_data.get("title")
                        ep_pv_cover = ep_pv_data.get("cover")
                        ep_pv_url = ep_pv_data.get("share_url")
                        ep_pv_avid = ep_pv_data.get("aid")
                        ep_pv_bvid = biliBV.encode(ep_pv_avid)
                        ep_pv_dt = {
                            "title": ep_pv_title,
                            "image": ep_pv_cover,
                            "url": ep_pv_url,
                            "bvid": ep_pv_bvid,
                            "avid": self.av + str(ep_pv_avid),
                            "测试": "2"
                        }
                        ep_pv_ls.append(ep_pv_dt)
                    for ep_data in episodes_data:
                        ep_title = ep_data.get("long_title")
                        ep_cover = ep_data.get("cover")
                        ep_url = ep_data.get("share_url")
                        ep_avid = ep_data.get("aid")
                        ep_bvid = biliBV.encode(ep_avid)
                        ep_volume = ep_data.get("title")
                        ep_dt = {
                            "title": ep_title,
                            "image": ep_cover,
                            "url": ep_url,
                            "bvid": ep_bvid,
                            "avid": self.av + str(ep_avid),
                            "volume": ep_volume,
                        }

                        ep_ls.append(ep_dt)
                    data = {"title": title, "cover": md_cover, "url": md_url, "states": 1, "ep": ep_ls,
                            "pv": ep_pv_ls, }
                    return data
            else:
                for ep_data in episodes_data:
                    ep_title = ep_data.get("long_title")
                    ep_cover = ep_data.get("cover")
                    ep_url = ep_data.get("share_url")
                    ep_avid = ep_data.get("aid")
                    ep_bvid = biliBV.encode(ep_avid)
                    ep_volume = ep_data.get("title")
                    ep_dt = {
                        "title": ep_title,
                        "image": ep_cover,
                        "url": ep_url,
                        "bvid": ep_bvid,
                        "avid": self.av + str(ep_avid),
                        "volume": ep_volume,
                    }
                    ep_ls.append(ep_dt)
                data = {"title": title, "cover": md_cover, "url": md_url, "states": 1, "ep": ep_ls}
                return data
        else:
            episodes_pv_data = eps_data.get("result").get("section")
            if len(episodes_pv_data) != 0:
                for eps_pv_data in episodes_pv_data:
                    for ep_pv_data in eps_pv_data.get("episodes"):
                        ep_pv_title = ep_pv_data.get("long_title")
                        if ep_pv_title == "":
                            ep_pv_title = ep_pv_data.get("title")
                        ep_pv_cover = ep_pv_data.get("cover")
                        ep_pv_url = ep_pv_data.get("share_url")
                        ep_pv_avid = ep_pv_data.get("aid")
                        ep_pv_bvid = biliBV.encode(ep_pv_avid)
                        ep_pv_dt = {
                            "title": ep_pv_title,
                            "image": ep_pv_cover,
                            "url": ep_pv_url,
                            "bvid": ep_pv_bvid,
                            "avid": self.av + str(ep_pv_avid),
                        }
                        ep_pv_ls.append(ep_pv_dt)
                    data = {"title": title, "cover": md_cover, "url": md_url, "states": 0, "pv": ep_pv_ls}
                    return data


def mian():
    a = "BV1nx411w7rp"
    av = "av216845"
    d_bv = "https://www.bilibili.com/video/BV1DP4y197WS/?spm_id_from=333.851.b_7265636f6d6d656e64.2"
    s_bv = "https://www.bilibili.com/video/BV1K24y1k7XA/?spm_id_from=333.851.b_7265636f6d6d656e64.3"
    url = "www.hecady.com/ssadasdasd"
    text = "sdfsdasda.sad561as5646"
    bv_id = "BV1QM41167tFadasdadsa"
    wsx_ss = "https://www.bilibili.com/bangumi/play/ss43148?from_spmid=666.14.0.0"
    wsx_ep = "https://www.bilibili.com/bangumi/play/ep680471"
    sx_ss = "https://www.bilibili.com/bangumi/play/ss42652?from_spmid=666.14.0.0"
    ep_id = "https://www.bilibili.com/bangumi/play/ep567775?from_spmid=666.4.banner.3"
    web_md = "https://www.bilibili.com/bangumi/media/md28339205/?spm_id_from=666.25.b_6d656469615f6d6f64756c65.2"
    web_ep = "https://www.bilibili.com/bangumi/play/ep670659?from_spmid=666.19.0.0"
    web_md1 = "https://www.bilibili.com/bangumi/media/md28339205/?spm_id_from=666.25.b_6d656469615f6d6f64756c65.2"
    ss_vide = "https://www.bilibili.com/bangumi/play/ss28324?from_spmid=666.25.series.0&from_outer_spmid=666.14.0.0"
    re0_ep = "https://www.bilibili.com/bangumi/play/ep330798?from_spmid=666.25.episode.0&from_outer_spmid=333.337.0.0"
    pv_ep = "https://www.bilibili.com/bangumi/play/ep480970?from_spmid=666.25.titbit.0&from_outer_spmid=666.4.banner.1"
    dianyin_ep = "https://www.bilibili.com/bangumi/play/ep514384?from_spmid=666.19.0.0"
    pv_md = "https://www.bilibili.com/bangumi/media/md28339716/?spm_id_from=666.25.b_6d656469615f6d6f64756c65.2"

    start = time.time()
    cover = BilibiliCover(pv_md)
    # print(cover.get_video_id())
    # print(cover.handleEpisodeResult())
    # print(cover.handleEpisodeResult())
    print(cover.handleMdResult())
    end = time.time()
    print(end - start)


mian()
