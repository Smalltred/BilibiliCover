#!/usr/bin/python
# -- coding: utf-8 --
# @Author : Small_tred 
# @Time : 2022/3/25 13:54
import requests
import re
import biliBV


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


def regexBv(true_url):
    """匹配BV号"""
    bv_id = re.search(r'(BV.*?).{10}', true_url)
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
    """匹配SS号"""
    ss_id = re.search(r"(ss.*?)\d+", true_url)
    if ss_id is not None:
        return ss_id.group(0)
    else:
        return None


def regexMd(true_url):
    """匹配Med号"""
    med_id = re.search(r"(md.*?)\d+", true_url)
    if med_id is not None:
        return med_id.group(0)
    else:
        return None


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


def requestsMdVideoApi(mdid):
    api = "https://api.bilibili.com/pgc/review/user?media_id="
    response = requests.get(api + mdid).json()
    if response["code"] == 0:
        return response


def requestsAllVideoApi(ssid):
    api = "https://api.bilibili.com/pgc/web/season/section?season_id="
    response = requests.get(api + ssid).json()
    if response["code"] == 0:
        return response


def handleVideoBvResult(response_result):
    """根据BV号 判断是否有分P 是返回全部分P的信息 否返回该视频的封面"""
    av = "av"
    bilibili = "https://www.bilibili.com/"
    ls = []
    if response_result is not None:
        if response_result.get("data").get("ugc_season") is not None:
            if len(response_result.get("data").get("ugc_season").get("sections")) != 0:
                for vds in response_result.get("data").get("ugc_season").get("sections"):
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
                            "url": bilibili + vd_bvid,
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
                "image": vd_cover,
                "bvid": vd_bvid,
                "avid": av + str(vd_avid),
                "url": bilibili + vd_bvid,
            }
            return data


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
                        "image": ep_cover,
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
                                            "image": ep_pv_cover,
                                            "bvid": ep_pv_bvid,
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
                            "image": ep_pv_cover,
                            "bvid": ep_pv_bvid,
                            "avid": av + str(ep_pv_avid),
                            "url": ep_pv_url,
                        }
                        return data


def handleSsResult(response_result, ssid):
    av = "av"
    if response_result is not None:
        if len(response_result.get("result").get("episodes")) != 0:
            if len(response_result.get("result").get("seasons")) != 0:
                for sss in response_result.get("result").get("seasons"):
                    if sss.get("season_id") == int(ssid):
                        for eps in response_result.get("result").get("episodes"):
                            if sss.get("new_ep").get("id") == eps.get("id"):
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
                                }
                                return data
        else:
            return "番剧是不是还没上线啊"


def handleMdResult(response_result):
    av = "av"
    ep_ls = []
    ep_pv_ls = []
    if response_result is not None:
        ssid = response_result.get("result").get("media").get("season_id")
        title = response_result.get("result").get("media").get("title")
        md_cover = response_result.get("result").get("media").get("cover")
        md_url = response_result.get("result").get("media").get("share_url")
        if requestsAllVideoApi(str(ssid)) is not None:
            eps_data = requestsAllVideoApi(str(ssid))
            if eps_data.get("result").get("main_section") is not None:
                episodes_data = eps_data.get("result").get("main_section").get("episodes")
                episodes_pv_data = eps_data.get("result").get("section")
                if len(episodes_pv_data) != 0:
                    for eps_pv_data in episodes_pv_data:
                        for ep_pv_data, i in zip(eps_pv_data.get("episodes"), range((len(eps_pv_data)))):
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
                                "avid": av + str(ep_pv_avid),
                            }
                            ep_pv_ls.append(ep_pv_dt)
                        for ep_data, j in zip(episodes_data, range(len(episodes_data))):
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
                                "avid": av + str(ep_avid),
                                "volume": ep_volume,
                            }

                            ep_ls.append(ep_dt)
                        data = {"title": title, "cover": md_cover, "url": md_url, "ep": ep_ls, "pv": ep_pv_ls, }
                        return data
                else:
                    for ep_data, j in zip(episodes_data, range(len(episodes_data))):
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
                            "avid": av + str(ep_avid),
                            "volume": ep_volume,
                        }
                        ep_ls.append(ep_dt)
                    data = {"title": title, "cover": md_cover, "url": md_url, "ep": ep_ls, "pv": "", }
                    return data
            else:
                data = {"title": title, "cover": md_cover, "url": md_url}
                return data


def main(content):
    """入口"""
    data = handleUrl(content)
    if data is not None:
        if regexBv(data) is not None:
            bvid = regexBv(data)
            if requestsBvVideoApi(bvid) is not None:
                result = requestsBvVideoApi(bvid)
                print(f"获取成功.bv号: {bvid}")
                return handleVideoBvResult(result)
        elif regexAv(data) is not None:
            bvid = regexAv(data)
            if requestsBvVideoApi(bvid) is not None:
                result = requestsBvVideoApi(bvid)
                av = biliBV.decode(bvid)
                print(f"获取成功.av号: {av}")
                return handleVideoBvResult(result)
        elif regexEp(data) is not None:
            epid = regexEp(data)
            if requestsEpVideoApi(epid) is not None:
                result = requestsEpVideoApi(epid)
                print(f"获取成功.ep号: {epid}")
                return handleEpisodeResult(result, epid)
        elif regexSs(data) is not None:
            ssid = regexSs(data)[2:]
            result = requestsSsVideoApi(ssid)
            print(f"获取成功.ss号: {ssid}")
            return handleSsResult(result, ssid)
        elif regexMd(data) is not None:
            mdid = regexMd(data)[2:]
            result = requestsMdVideoApi(mdid)
            print(f"获取成功.md号: {mdid}")
            return handleMdResult(result)

    else:
        if regexBv(content) is not None:
            bvid = regexBv(content)
            if requestsBvVideoApi(bvid) is not None:
                result = requestsBvVideoApi(bvid)
                print(f"获取成功.bv号: {bvid}")
                return handleVideoBvResult(result)
        elif regexAv(content) is not None:
            bvid = regexAv(content)
            if requestsBvVideoApi(bvid) is not None:
                result = requestsBvVideoApi(bvid)
                av = biliBV.decode(bvid)
                print(f"获取成功.av号: {av}")
                return handleVideoBvResult(result)
        elif regexEp(content) is not None:
            epid = regexEp(content)
            if requestsEpVideoApi(epid) is not None:
                result = requestsEpVideoApi(epid)
                print(f"获取成功.ep号: {epid}")
                return handleEpisodeResult(result, epid)
        elif regexSs(content) is not None:
            ssid = regexSs(content)[2:]
            if requestsSsVideoApi(ssid) is not None:
                result = requestsSsVideoApi(ssid)
                print(f"获取成功.ss号: {ssid}")
                return handleSsResult(result, ssid)
        elif regexMd(content) is not None:
            mdid = regexMd(content)[2:]
            if requestsMdVideoApi(mdid) is not None:
                result = requestsMdVideoApi(mdid)
                print(f"获取成功.md号: {mdid}")
                return handleMdResult(result)


if __name__ == '__main__':
    print(main("https://www.bilibili.com/bangumi/media/md28237141/?spm_id_from=666.25.b_6d656469615f6d6f64756c65.2"))
