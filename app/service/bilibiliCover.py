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


# noinspection PyBroadException

class BilibiliCover:
    url = "https://www.bilibili.com/"
    av = "av"
    bv_api = "https://api.bilibili.com/x/web-interface/view?bvid="
    ep_api = "https://api.bilibili.com/pgc/view/web/season?ep_id="
    ss_api = "https://api.bilibili.com/pgc/view/web/season?season_id="
    md_api = "https://api.bilibili.com/pgc/review/user?media_id="
    md_all_api = "https://api.bilibili.com/pgc/web/season/section?season_id="
    id_type = None

    def __init__(self, content):
        self.content = content

    def get_video_id(self):
        """匹配文本中的链接 判断链接是否重定向 获取重定向后的链接"""
        try:
            b_url = re.search(r"[a-zA-z]+://[^\s]*", self.content).group(0)
            response = requests.get(b_url).url
            return self.regexId(response)
        except Exception as e:
            return self.regexId(self.content)

    def regexId(self, string):
        id_type = None
        bv_id = self.regexBv(string)
        av_id = self.regexAv(string)
        ep_id = self.regexEp(string)
        ss_id = self.regexSs(string)
        md_id = self.regexMd(string)
        if bv_id:
            id_type = "bv"
        elif av_id:
            id_type = "bv"
            bv_id = biliBV.encode(av_id)
        elif ep_id:
            id_type = "ep"
        elif ss_id:
            id_type = "ss"
        elif md_id:
            id_type = "md"
        self.id_type = id_type
        return locals()[f"{id_type}_id"]

    @staticmethod
    def regexBv(string):
        """匹配BV号"""
        regex = re.compile(r'(BV.*?).{10}', re.I)
        bv_id = regex.search(string)
        if bv_id:
            return bv_id.group(0)

    @staticmethod
    def regexAv(string):
        """匹配av号"""
        regex = re.compile(r"(av.*?)\d+", re.I)
        av_id = regex.search(string)
        if av_id:
            return av_id.group(0)[2:]

    @staticmethod
    def regexEp(string):
        regex = re.compile(r"(ep.*?)\d+", re.I)
        ep_id = regex.search(string)
        if ep_id:
            return ep_id.group(0)[2:]

    @staticmethod
    def regexSs(string):
        """匹配SS号"""
        regex = re.compile(r"(ss.*?)\d+", re.I)
        ss_id = regex.search(string)
        if ss_id:
            return ss_id.group(0)[2:]

    @staticmethod
    def regexMd(string):
        """匹配Med号"""
        regex = re.compile(r"(md.*?)\d+")
        md_id = regex.search(string)
        if md_id:
            return md_id.group(0)[2:]

    def handleBvResult(self, bv_id):
        """根据BV号 判断是否有分P 是返回全部分P的信息 否返回该视频的封面"""
        data = []
        response = requests.get(self.bv_api + bv_id).json()
        # 多p判断
        if response.get("data").get("ugc_season") is not None:
            for vds in response.get("data").get("ugc_season").get("sections"):
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
                    data.append(temp)
                result = {"code": 200, "msg": "success", "self.id_type": self.id_type, "data": data}
                return result
        # 单p判断
        else:
            vd_data = response.get("data")
            vd_title = vd_data.get("title")
            vd_cover = vd_data.get("pic")
            vd_bvid = vd_data.get("bvid")
            vd_avid = vd_data.get("aid")
            result = {"code": 200, "msg": "success", "id_type": self.id_type, "data": {
                "title": vd_title,
                "image": vd_cover,
                "bvid": vd_bvid,
                "avid": self.av + str(vd_avid),
                "url": self.url + vd_bvid,
            }}
            return result

    def handleEpResult(self, ep_id):

        """
        1.判断请求内容是否存在
        2.判断番剧是否上线  是 继续判断是(pv或小剧场)还是番剧 否 判断是否为(pv或小剧场)"""

        response = requests.get(self.ep_api + ep_id).json()
        # 判断番剧是否上线 0 没上线 1 上线
        if len(response.get("result").get("episodes")) != 0:
            for eps in response.get("result").get("episodes"):
                # 判断是番剧封面还是PV封面
                if eps.get("id") == int(ep_id):
                    ep_title = eps.get("share_copy")
                    ep_cover = eps.get("cover")
                    ep_bvid = eps.get("bvid")
                    ep_avid = eps.get("aid")
                    ep_url = eps.get("share_url")
                    result = {"code": 200, "msg": "success", "id_type": self.id_type, "data": {
                        "title": ep_title,
                        "image": ep_cover,
                        "bvid": ep_bvid,
                        "avid": self.av + str(ep_avid),
                        "url": ep_url,
                    }}
                    return result
        # 判断是番剧封面还是PV封面
        else:
            for pvs in response.get("result").get("section"):
                for pv in (pvs.get("episodes")):
                    if pv.get("id") == int(ep_id):
                        ep_pv_title = pv.get("share_copy")
                        ep_pv_cover = pv.get("cover")
                        ep_pv_bvid = pv.get("bvid")
                        ep_pv_avid = pv.get("aid")
                        ep_pv_url = pv.get("share_url")
                        result = {"code": 200, "msg": "success", "id_type": self.id_type, "data": {
                            "title": ep_pv_title,
                            "image": ep_pv_cover,
                            "bvid": ep_pv_bvid,
                            "avid": self.av + str(ep_pv_avid),
                            "url": ep_pv_url,
                        }}
                        return result

    def handleSsResult(self, ss_id):
        response = requests.get(self.ss_api + ss_id).json()
        # 上线了则
        if len(response.get("result").get("episodes")) != 0:
            if response.get("result").get("seasons") is not None:
                for ss in response.get("result").get("seasons"):
                    if ss.get("season_id") == int(ss_id):
                        for eps in response.get("result").get("episodes"):
                            if ss.get("new_ep").get("id") == eps.get("id"):
                                ep_title = eps.get("share_copy")
                                ep_cover = eps.get("cover")
                                ep_bvid = eps.get("bvid")
                                ep_avid = eps.get("aid")
                                ep_url = eps.get("share_url")
                                result = {"code": 200, "msg": "success", "id_type": self.id_type, "data": {
                                    "title": ep_title,
                                    "image": ep_cover,
                                    "bvid": ep_bvid,
                                    "avid": self.av + str(ep_avid),
                                    "url": ep_url,
                                }}
                                return result
        # 没上线则
        else:
            if len(response.get("result").get("section")) != 0:
                for pvs in response.get("result").get("section"):
                    for pv in (pvs.get("episodes")):
                        ep_title = pv.get("share_copy")
                        ep_cover = pv.get("cover")
                        ep_bvid = pv.get("bvid")
                        ep_avid = pv.get("aid")
                        ep_url = pv.get("share_url")
                        data = {"code": 200, "msg": "success", "id_type": self.id_type, "data": {
                            "title": ep_title,
                            "image": ep_cover,
                            "bvid": ep_bvid,
                            "avid": self.av + str(ep_avid),
                            "url": ep_url,
                        }}
                        return data

    def handleMdResult(self, md_id):
        ep_ls = []
        ep_pv_ls = []
        response = requests.get(self.md_api + md_id).json()
        ssid = response.get("result").get("media").get("season_id")
        title = response.get("result").get("media").get("title")
        cover = response.get("result").get("media").get("cover")
        url = response.get("result").get("media").get("share_url")
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
                    data = {"code": 200, "msg": "success", "id_type": self.id_type,
                            "data": {"md_title": title, "md_cover": cover, "md_url": url, "states": 1, "eps": ep_ls,
                                     "pvs": ep_pv_ls}}
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
                result = {"code": 200, "msg": "success", "id_type": self.id_type,
                          "data": {"md_title": title, "md_cover": cover, "md_url": url, "states": 1, "eps": ep_ls}}

                return result
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
                    result = {"code": 200, "msg": "success", "id_type": self.id_type,
                              "data": {"md_title": title, "md_cover": cover, "md_url": url, "states": 0, "pvs": ep_pv_ls}}
                    return result

    def get_cover(self):
        try:
            video_id = self.get_video_id()
            if self.id_type == "bv":
                return self.handleBvResult(video_id)
            elif self.id_type == "ss":
                return self.handleSsResult(video_id)
            elif self.id_type == "ep":
                return self.handleEpResult(video_id)
            elif self.id_type == "md":
                return self.handleMdResult(video_id)
        except TypeError as e:
            print("错误 {}".format(e))
            error = {"code": 403, "msg": "这好像不是B站的链接哦~"}
            return error
