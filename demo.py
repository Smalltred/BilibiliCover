#!/usr/bin/python
# -- coding: utf-8 --
# @Author : Small_tred 
# @Time : 2022/3/23 23:55
import requests
import re
from biliBV import encode
import json
import ast


def requestsVideoAvApi(avid):
    api = "https://api.bilibili.com/x/web-interface/view?aid="
    response = requests.get(api + avid).json()
    if response["code"] == 0:
        return response
    else:
        return None


def requestsVideoBvApi(bvid):
    api = "https://api.bilibili.com/x/web-interface/view?bvid="
    response = requests.get(api + bvid)
    if response["code"] == 0:
        return response
    else:
        return None


def requestsDramaApi(epid):
    api = "https://api.bilibili.com/pgc/view/web/season?ep_id="
    response = requests.get(api + epid)
    if response["code"] == 0:
        return response
    else:
        return None


def getVideoData(video_url):
    b_url = re.search(r"[a-zA-z]+://[^\s]*", video_url)
    if b_url is not None:
        true_url = requests.get(b_url.group(0), allow_redirects=False)
        if true_url.status_code == 302:
            url = requests.get(b_url.group(0)).url
            bv_id = re.search(r'(BV.*?)\?', url)
            if bv_id is not None:
                print(bv_id.group(1))
                return requestsVideoBvApi(bv_id.group(1))
            else:
                return None
        else:
            url = requests.get(b_url.group(0)).url
            bv_id = re.search(r'(BV.*?)\?', url)
            if bv_id is not None:
                print(bv_id.group(1))
                return requestsVideoBvApi(bv_id.group(1))
            else:
                av_id = re.search(r"(av.*?)\d+", video_url)
                if av_id is not None:
                    print(av_id.group(0))
                    bvid = encode(av_id.group(0))
                    return requestsVideoAvApi(bvid)

    else:
        bv_id = re.search(r'(BV.*?).{10}', video_url)
        if bv_id is not None:
            print(bv_id.group(0))
            return requestsVideoBvApi(bv_id.group(0))
        else:
            av_id = re.search(r"(av.*?)\d+", video_url)
            if av_id is not None:
                print(av_id.group(0))
                bvid = encode(av_id.group(0))
                return requestsVideoAvApi(bvid)
            else:
                return None


def getDramaData(drama_url):
    b_url = re.search(r"[a-zA-z]+://[^\s]*", drama_url)
    if b_url is not None:
        true_url = requests.get(b_url.group(0), allow_redirects=False)
        if true_url.status_code == 302:
            url = requests.get(b_url.group(0)).url
            ep_id = re.search(r"\d+", url)
            print(ep_id.group(0))
            return requestsDramaApi(ep_id.group(0))
        else:
            ep_id = re.search(r"\d+", drama_url)
            if ep_id is not None:
                print(ep_id.group(0))
                return requestsDramaApi(ep_id.group(0))

    else:
        ep_id = re.search(r"\d+", drama_url)
        if ep_id is not None:
            print(ep_id.group(0))
            return requestsDramaApi(ep_id.group(0))


# getDramaData("【《青春猪头少年不会梦到兔女郎学姐》 第1话 学姐是兔女郎-哔哩哔哩番剧】https://b23.tv/ep251076")
# getDramaData("https://www.bilibili.com/bangumi/play/ep449777?from_spmid=666.4.0.0")
# getDramaData("ep450007")
# getVideoData("av679312311148aasdad")
# requestsVideoAvApi("av679312311148")
# print(requestsVideoAvApi("av679312311148"))