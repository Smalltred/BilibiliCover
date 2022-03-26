#!/usr/bin/python
# -- coding: utf-8 --
# @Author : Small_tred 
# @Time : 2022/3/25 13:54
import requests
import re
import biliBV


def regexBv(true_url):
    """匹配BV号"""
    bv_id = re.search(r'(BV.*?).\w*', true_url)
    if bv_id is not None:
        return bv_id.group(0)


def regexAv(true_url):
    """匹配av号"""
    av_id = re.search(r"(av.*?)\d+", true_url)
    if av_id is not None:
        bv_id = biliBV.encode(av_id.group(0))
        return bv_id


def regexEp(true_url):
    """匹配ep号"""
    ep_id = re.search(r"(ep.*?)\d+", true_url)
    if ep_id is not None:
        return ep_id.group(0)[2:]


def regexSs(true_url):
    pass
    # 匹配SS号
    # ss_id = re.search(r"(ss.*?)\d+", true_url)
    # if ss_id is not None:
    #     return ss_id.group(0)
    # else:
    #     return None


def regexMed(true_url):
    pass
    # 匹配Med号
    # med_id = re.search(r"\d+", true_url)
    # if med_id is not None:
    #     return med_id.group(0)
    # else:
    #     return None


def handleUrl(in_url):
    """判断链接是否为跳转 获取真实链接"""
    b_url = re.search(r"[a-zA-z]+://[^\s]*", in_url)
    if b_url is not None:
        response = requests.get(b_url.group(0), allow_redirects=False)
        if response.status_code == 302:
            t_url = requests.get(b_url.group(0)).url
            return t_url
        elif response.status_code == 301:
            t_url = requests.get(b_url.group(0)).url
            return t_url
        else:
            return b_url.group(0)

# 请求API
def requestsBvVideoApi(bvid):
    api = "https://api.bilibili.com/x/web-interface/view?bvid="
    response = requests.get(api + bvid).json()
    if response["code"] == 0:
        return response


def requestsEpVideoApi(epid):
    api = "https://api.bilibili.com/pgc/view/web/season?ep_id="
    response = requests.get(api + epid).json()
    if response["code"] == 0:
        return response


def requestsSsVideoApi(ssid):
    api = "https://api.bilibili.com/pgc/view/web/season?season_id="
    response = requests.get(api + ssid).json()
    if response["code"] == 0:
        return response


def handleVideoBvResult(response_result, vid):
    """根据BV号 判断是否有分P 是返回全部分P的信息 否返回该视频的封面"""
    av = "av"
    bilibili = "https://www.bilibili.com/"
    ls = []
    if response_result is not None:
        if response_result.get("data").get("ugc_season") is not None:
            for vds in response_result.get("data").get("ugc_season").get("sections"):
                for vd, i in zip(vds.get("episodes"), range(len(vds.get("episodes")))):
                    vd_title = vd.get("title")
                    vd_cover = vd.get("arc").get("pic")
                    vd_bvid = vd.get("bvid")
                    vd_avid = vd.get("aid")
                    data = {
                        i: {
                            "title": vd_title,
                            "images": vd_cover,
                            "bvid": vd_bvid,
                            "avid": av + str(vd_avid),
                            "url": bilibili + vd_bvid,
                        }
                    }
                    ls.append(data)
                return ls
        else:
            vd_data = response_result.get("data")
            vd_title = vd_data.get("title")
            vd_cover = vd_data.get("pic")
            vd_bvid = vd_data.get("bvid")
            vd_avid = vd_data.get("aid")
            data = {
                "title": vd_title,
                "images": vd_cover,
                "bvid": vd_bvid,
                "avid": av + str(vd_avid),
                "url": bilibili + vd_bvid,
            }
            return data
    else:
        return "Not"


def handleEpisodeResult(response_result, epid):
    """1.判断请求内容是否存在 2.判断番剧是否上线  是继续判断是pv/小剧场还是番剧 否 判断是否为pv/小剧场"""
    av = "av"
    if response_result is not None:
        if len(response_result.get("result").get("episodes")) != 0:
            for eps in response_result.get("result").get("episodes"):
                if eps.get("id") == int(epid):
                    ep_title = eps.get("share_copy")
                    ep_cover = eps.get("cover")
                    ep_bvid = eps.get("bvid")
                    ep_avid = eps.get("aid")
                    ep_url = eps.get("share_url")
                    data = {
                        "title": ep_title,
                        "images": ep_cover,
                        "bvid": ep_bvid,
                        "avid": av + str(ep_avid),
                        "url": ep_url,
                    }
                    return data
                else:
                    if response_result.get("result").get("section") is not None:
                        if len(response_result.get("result").get("section")) != 0:
                            for pvs in response_result.get("result").get("section"):
                                for pv in (pvs.get("episodes")):
                                    if pv.get("id") == int(epid):
                                        ep_pv_title = pv.get("share_copy")
                                        ep_pv_cover = pv.get("cover")
                                        ep_pv_bvid = pv.get("bvid")
                                        ep_pv_avid = pv.get("aid")
                                        ep_pv_url = pv.get("share_url")
                                        data = {
                                            "title": ep_pv_title,
                                            "images": ep_pv_cover,
                                            "bvid": ep_pv_avid,
                                            "avid": av + str(ep_pv_avid),
                                            "url": ep_pv_url,
                                        }
                                        return data
        else:
            for pvs in response_result.get("result").get("section"):
                for pv in pvs.get("episodes"):
                    if pv.get("id") == int(epid):
                        ep_pv_title = pv.get("share_copy")
                        ep_pv_cover = pv.get("cover")
                        ep_pv_bvid = pv.get("bvid")
                        ep_pv_avid = pv.get("aid")
                        ep_pv_url = pv.get("share_url")
                        data = {
                            "title": ep_pv_title,
                            "images": ep_pv_cover,
                            "bvid": ep_pv_avid,
                            "avid": av + str(ep_pv_avid),
                            "url": ep_pv_url,
                        }
                        return data


def handleSsResult(response_result, ssid):
    pass


def handleMediaResult(response_result):
    pass


def main(content):
    """入口"""
    data = handleUrl(content)
    if data is not None:
        if regexBv(data) is not None:
            bvid = regexBv(data)
            if requestsBvVideoApi(bvid) is not None:
                print(f"获取成功.bv号: {bvid}")
                result = requestsBvVideoApi(bvid)
                return handleVideoBvResult(result, bvid)
        elif regexAv(data) is not None:
            bvid = regexAv(data)
            if requestsBvVideoApi(bvid) is not None:
                print(f"获取成功.bv号: {bvid}")
                result = requestsBvVideoApi(bvid)
                return handleVideoBvResult(result, bvid)
        elif regexEp(data) is not None:
            epid = regexEp(data)
            if requestsEpVideoApi(epid) is not None:
                print(f"获取成功.ep号: {epid}")
                result = requestsEpVideoApi(epid)
                return handleEpisodeResult(result, epid)

    else:
        if regexBv(content) is not None:
            bvid = regexBv(content)
            if requestsBvVideoApi(bvid) is not None:
                print(f"获取成功.bv号: {bvid}")
                result = requestsBvVideoApi(bvid)
                return handleVideoBvResult(result, bvid)
        elif regexAv(content) is not None:
            bvid = regexAv(content)
            if requestsBvVideoApi(bvid) is not None:
                print(f"获取成功.bv号: {bvid}")
                result = requestsBvVideoApi(bvid)
                return handleVideoBvResult(result, bvid)
        elif regexEp(content) is not None:
            epid = regexEp(content)
            if requestsEpVideoApi(epid) is not None:
                print(f"获取成功.ep号: {epid}")
                result = requestsEpVideoApi(epid)
                return handleEpisodeResult(result, epid)


if __name__ == '__main__':
    txt = open("测试链接.text", "r", encoding="UTF-8").read().splitlines()
    for i in txt:
        print(main(i))
