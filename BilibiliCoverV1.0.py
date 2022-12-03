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

    def __init__(self, content):
        self.content = content
        self.data = ""

    def handleData(self):
        """判断链接是否为跳转 获取真实链接"""
        try:
            b_url = re.search(r"[a-zA-z]+://[^\s]*", self.content).group(0)
            response = requests.get(b_url)
            if response.status_code == 302:
                real_url = requests.get(b_url, allow_redirects=False).url
                return real_url
            else:
                return b_url
        except Exception as e:
            e = None
            return e

    def get_id(self):
        if self.handleData() is not None:
            self.data = self.handleData()
            video_id = self.matchAll()
            return video_id
        else:
            self.data = self.content
            video_id = self.matchAll()
            return video_id

    def matchAll(self):
        bvid = self.regexBv(self.data)
        avid = self.regexAv(self.data)
        epid = self.regexEp(self.data)
        ssid = self.regexSs(self.data)
        mdid = self.regexMd(self.data)
        if bvid is not None:
            return bvid
        elif avid is not None:
            return avid
        elif epid is not None:
            return epid
        elif ssid is not None:
            return ssid
        elif mdid is not None:
            return mdid
        else:
            return "请检查输入是否正确"

    @staticmethod
    def regexBv(content):
        """匹配BV号"""
        try:
            regex = re.compile(r'(BV.*?).{10}', re.I)
            bv_id = regex.search(content).group(0)
            return bv_id, "bv"
        except Exception as e:
            return None

    @staticmethod
    def regexAv(content):
        """匹配av号"""
        try:
            regex = re.compile(r"(av.*?)\d+", re.I)
            av_id = regex.search(content).group(0)[2:]
            bv_id = biliBV.encode(av_id)
            return bv_id, "bv"
        except Exception as e:
            return None

    @staticmethod
    def regexEp(content):
        """匹配ep号"""
        try:
            regex = re.compile(r"(ep.*?)\d+", re.I)
            ep_id = regex.search(content).group(0)[2:]
            return ep_id, "ep"
        except Exception as e:
            return None

    @staticmethod
    def regexSs(content):
        """匹配SS号"""
        try:
            regex = re.compile(r"(ss.*?)\d+", re.I)
            ss_id = regex.search(content).group(0)
            return ss_id, "ss"
        except Exception as e:
            return None

    @staticmethod
    def regexMd(content):
        """匹配Med号"""
        try:
            regex = re.compile(r"(md.*?)\d+")
            md_id = re.search(content).group(0)
            return md_id, "md"
        except Exception as e:
            return None


def main():
    a = ""
    av = "av216845"
    url = "www.hecady.com/ssadasdasd"
    text = "sdfsdasda.sad561as5646"
    bv_id = "BV1QM41167tFadasdadsa"
    ep_id = "https://www.bilibili.com/bangumi/play/ep567775?from_spmid=666.4.banner.3"
    bv_url = "https://www.bilibili.com/video/BV1QM41167tF/?spm_id_from=333.851.b_7265636f6d6d656e64.1"
    cover = BilibiliCover(ep_id)
    print(cover.get_id())


main()
