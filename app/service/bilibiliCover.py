#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
# @Time    : 2023/4/14 6:49
# @Author  : Small tred
# @FileName: bilibiliCover.py
# @Software: PyCharm
# @Blog    : https://www.hecady.com
import requests
import re


class BiliBv:
    def __init__(self):
        self.table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
        self.tr = {}
        for i in range(58):
            self.tr[self.table[i]] = i
        self.s = [11, 10, 3, 8, 4, 6]
        self.xor = 177451812
        self.add = 8728348608

    # BV转AV
    def bv2av(self, x: str) -> int:
        if len(x) == 11:
            x = "BV1" + x[2:]
        r = 0
        for i in range(6):
            r += self.tr[x[self.s[i]]] * 58 ** i
        return (r - self.add) ^ self.xor

    # AV转BV
    def av2bv(self, x: int) -> str:
        y = int(x)
        y = (y ^ self.xor) + self.add
        r = list('BV1  4 1 7  ')
        for i in range(6):
            r[self.s[i]] = self.table[y // 58 ** i % 58]
        return ''.join(r)


class BilibiliCover(BiliBv):
    __apis = {
        "bv": "https://api.bilibili.com/x/web-interface/view?bvid=",
        "av": "https://api.bilibili.com/x/web-interface/view?bvid=",
        "ep": "https://api.bilibili.com/pgc/view/web/season?ep_id=",
        "ss": "https://api.bilibili.com/pgc/view/web/season?season_id=",
        "md": "https://api.bilibili.com/pgc/review/user?media_id="
    }
    __url = "https://www.bilibili.com/"

    __av_prefix = "av"

    __errors = [
        {"code": -404, "message": "请检查内容是否包含视频ID"},
        {'code': -400, 'message': '获取封面失败或稿件不存在'},
        {"code": -1, 'message': "请求失败"}
    ]

    __regex_error = {"code": -404, "message": "请检查内容是否包含视频ID"}
    __response_error = {'code': -400, 'message': '获取封面失败或稿件不存在'}
    __requests_error = {"code": -1, 'message': "请求失败"}

    __success = {
        "code": 200,
        "message": "获取封面成功"
    }

    video_id_type = None

    def __init__(self, string: str) -> None:
        super().__init__()
        self.string: str = string
        self.api_response: dict = {}
        self.video_id = None

    def getVideoId(self):
        """
        正则匹配 内容是否包含视频ID
        :return: BV1S24y1w7rU、av号匹配成功转为bv号、ep743051、ss26266、md28229233
        :return {"code": -404, "message": "请检查内容是否包含视频ID"}
        ep号 ss号 md号 不带前缀
        """
        id_dict = {
            "bv": self.__regexBv,
            "av": self.__regexAv,
            "ep": self.__regexEp,
            "ss": self.__regexSs,
            "md": self.__regexMd
        }
        url_regex_result = self.__regexUrl()
        for video_id_type, regex_func in id_dict.items():
            id_regex_result = regex_func(url_regex_result)
            if id_regex_result:
                self.video_id_type = video_id_type
                return id_regex_result
        return self.__regex_error

    @staticmethod
    def __redirectUrl(url):
        """
        对b23.tv进行重定向，获取真实地址
        :param url: 【xxx-哔哩哔哩】 https://b23.tv/hMwMJ70
        :return:
        """
        r = requests.get(url, allow_redirects=False)
        if r.status_code == 301 or r.status_code == 302:
            location = r.headers['Location']
            return location
        return None

    def __regexUrl(self):
        """
        1.判断是否为链接
        2.判断是否为b23.tv
        3.判断是否为bilibili.com
        4.判断是否为b23.tv重定向后的真实地址
        :return: https://www.bilibili.com/video/BV1S24y1w7rU/ or self.string
        """
        url = re.search(r"[a-zA-z]+://[^\s]*", self.string)
        if url:
            b23_pattern = r'https?://b23\.tv/[\w-]+'
            bilibili_pattern = r'https?://www\.bilibili\.com/[\w-]+'
            if re.match(b23_pattern, url.group(0)):
                result = self.__redirectUrl(url.group(0))
            elif re.match(bilibili_pattern, url.group(0)):
                result = url.group(0)
            else:
                result = self.string
        else:
            result = self.string
        return result

    def __regexAv(self, string: str) -> str:
        """匹配av号"""
        """自动转为bv号"""
        regex = re.compile(r"(av.*?)\d+", re.I)
        av_id = regex.search(string)
        if av_id:
            return self.av2bv(av_id.group(0)[2:])

    @staticmethod
    def __regexBv(string: str) -> str:
        """匹配BV号"""
        regex = re.compile(r'(BV.*?).{10}', re.I)
        bv_id = regex.search(string)
        if bv_id:
            return bv_id.group(0)

    @staticmethod
    def __regexEp(string: str) -> str:
        """匹配EP号"""
        regex = re.compile(r"(ep.*?)\d+", re.I)
        ep_id = regex.search(string)
        if ep_id:
            return ep_id.group(0)[2:]

    @staticmethod
    def __regexSs(string: str) -> str:
        """匹配SS号"""
        regex = re.compile(r"(ss.*?)\d+", re.I)
        ss_id = regex.search(string)
        if ss_id:
            return ss_id.group(0)[2:]

    @staticmethod
    def __regexMd(string: str) -> str:
        """匹配Med号"""
        regex = re.compile(r"(md.*?)\d+")
        md_id = regex.search(string)
        if md_id:
            return md_id.group(0)[2:]

    def requestApi(self) -> dict:
        """
        请求API 对传入的video_id进行检查
        :return: 成功返回 对应请求json对象 失败 返回响应错误代码
        :return {"code": -404, "message": "请检查内容是否包含视频ID"}
        :return {'code': -400, 'message': '获取封面失败'}
        """
        video_id = self.getVideoId()
        try:
            if video_id not in self.__errors:
                self.video_id = video_id
                api = self.__apis.get(self.video_id_type)
                response = requests.get(api + video_id).json()
                if response['code'] == 0:
                    return response
                else:
                    return self.__response_error
            else:
                return self.__regex_error
        except requests.exceptions.RequestException:
            return self.__requests_error

    def handleResponse(self) -> dict:
        handle_dict = {
            "bv": self.__handleBvResponse,
            "av": self.__handleBvResponse,
            "ep": self.__handleEpResponse,
            "ss": self.__handleSsResponse,
            'md': self.__handleMdResponse,
        }
        self.api_response = self.requestApi()
        if self.api_response not in self.__errors:
            return handle_dict.get(self.video_id_type)()
        return self.api_response

    #
    def __handleBvResponse(self):
        response = self.api_response
        if response.get('data'):
            bv_video_response = response.get("data")
            multi_video_response = bv_video_response.get('ugc_season')
            # 多P视频
            if multi_video_response:
                return self.__handleBvMultiResponse(bv_video_response)
            # 合集
            else:
                return self.__handleBvSingleResponse(bv_video_response)
        else:
            return self.api_response

    def __handleBvSingleResponse(self, video_data) -> dict:
        video_key = {"title", "pic", "bvid", "aid"}

        # 创建键名映射关系字典
        key_map = {"aid": "avid", "pic": "cover"}

        # 创建新字典，用新键名从旧字典中复制旧键的值
        result = {key_map.get(key, key): video_data.get(key) for key in video_data}

        result["avid"] = f"av{result['avid']}"
        result["url"] = self.__url + result["bvid"]

        video_type_info = {"is_multi_video": 0, "video_count": 1, "video_id_type": self.video_id_type}
        result["video_type_info"] = video_type_info

        # 仅保留需要的键
        result = {key: result[key] for key in video_key | {"avid", "cover", "video_type_info", "url"} if
                  key in result}

        return result

    def __handleBvMultiResponse(self, video_data) -> dict:
        url = self.__url
        video_key = {"title", "aid", "pic"}
        multi_video_data = video_data.get('ugc_season').get("sections")[0].get("episodes")
        current_bvid_result = self.__handleBvSingleResponse(video_data)

        # 创建键名映射关系字典
        key_map = {"aid": "avid", "pic": "cover"}

        def handleBvResult(video):
            # 创建新字典，用新键名从旧字典中复制旧键的值
            video_info = {key_map.get(key, key): video.get("arc").get(key) for key in video_key}

            # 添加新键值对
            video_info["bvid"] = video.get("bvid")
            video_info["url"] = url + video.get("bvid")
            video_info["cover"] = "https://www.bilibili.com/video/" + video_info["cover"]
            video_info["avid"] = f"av{video_info['avid']}"

            return video_info

        multi_video_result = [handleBvResult(video) for video in multi_video_data]
        video_type_info = {"is_multi_video": 1, "video_count": len(multi_video_result),
                           "video_id_type": self.video_id_type}

        result = {**current_bvid_result, "video_list": multi_video_result, "video_type_info": video_type_info}

        return result

    def __handleEpResponse(self):
        video_key = {"share_copy", "cover", "bvid", "aid", "link"}

        # 创建键名映射关系字典
        key_map = {"share_copy": "title", "aid": "avid", "link": "url"}

        def handleEpPvResult(video_data, ep_type):
            video_info = {}
            for video_data_key in video_data:
                if video_data_key.get("id") == int(self.video_id):
                    video_info = {key_map.get(key, key): video_data_key.get(key) for key in video_key}
                    break

            video_info["avid"] = f"av{video_info['avid']}"
            video_type_info = {"is_multi_video": 0, "video_count": 1, "video_id_type": self.video_id_type,
                               "type_name": ep_type}
            result = {**video_info, "video_type_info": video_type_info}
            return result

        is_pv_ep = "pv"
        response = self.api_response
        if response.get("result"):
            video_result = response.get("result")
            ep_video_result = video_result.get("episodes")
            pv_video_result = video_result.get("section")
            if pv_video_result:
                pv_video_result = pv_video_result[0].get("episodes")
            for ep_video_result_key in ep_video_result:
                if ep_video_result_key.get("id") == int(self.video_id):
                    is_pv_ep = "ep"
                    break
            if is_pv_ep == "ep":
                return handleEpPvResult(ep_video_result, is_pv_ep)
            else:
                return handleEpPvResult(pv_video_result, is_pv_ep)

    def __handleMdResponse(self):
        poster_video_key = {"link", "cover", "season_title"}

        # 创建键名映射关系字典
        poster_key_map = {"link": "poster_url", "cover": "poster_cover", "season_title": "poster_title"}

        video_key = {"link", "cover", "bvid", "aid", "long_title", "title"}
        video_key_map = {"link": "url", "aid": "avid", "long_title": "title"}

        def handleEpResult(video_info):
            if video_info:
                ep_video_info = [{video_key_map.get(key, key): j.get(key) for key in video_key} | {"volume": i + 1} for
                                 i, j in enumerate(video_info)]
                return ep_video_info
            return False

        def handlePvResult(video_info):
            if video_info:
                video_info = video_info[0].get("episodes")
                pv_video_info = [{video_key_map.get(key, key): j.get(key) for key in video_key} | {"pv": i + 1} for i, j
                                 in enumerate(video_info)]
                return pv_video_info
            return False

        response = self.api_response
        if response.get("result"):
            video_result = response.get("result").get("media")
            season_id = video_result.get("season_id")
            video_response = requests.get(self.__apis.get("ss") + str(season_id)).json().get("result")
            ep_video_result = video_response.get("episodes")
            pv_video_result = video_response.get("section")

            poster_video_info = {poster_key_map.get(key, key): video_response.get(key) for key in poster_video_key}
            video_type_info = {"is_multi_video": 0, "video_count": 1, "video_id_type": self.video_id_type}
            result = {
                **poster_video_info,
                "video_type_info": video_type_info
            }
            if handleEpResult(ep_video_result):
                result["eps"] = handleEpResult(ep_video_result)
                result["video_type_info"]["states"] = 1
                if handlePvResult(pv_video_result):
                    result["pvs"] = handlePvResult(pv_video_result)
            elif handlePvResult(pv_video_result):
                result["pvs"] = handlePvResult(pv_video_result)
                result["video_type_info"]["states"] = 0
            return result

    def __handleSsResponse(self):

        video_key = {"share_copy", "cover", "bvid", "aid", "share_url"}

        # 创建键名映射关系字典
        key_map = {"share_copy": "title", "aid": "avid", "share_url": "url"}

        def handleSsResult(video_data):
            result = {key_map.get(key, key): value for key, value in video_data.items() if key in video_key}
            result["avid"] = f"av{result['avid']}"
            video_type_info = {"is_multi_video": 0, "video_count": 1, "video_id_type": self.video_id_type}
            result['video_type_info'] = video_type_info
            return result

        response = self.api_response

        episodes = response.get("result").get("episodes")
        sections = response.get("result").get("section")

        for episode in episodes:
            if episode.get("id") == response.get("result").get("new_ep").get("id"):
                return handleSsResult(episode)

        for section in sections:
            for episode in section.get("episodes"):
                return handleSsResult(episode)

    def cover(self):
        return self.handleResponse()
