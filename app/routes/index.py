#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
# @Time    : 2023/3/14 19:13
# @Author  : Small tred
# @FileName: routes.py
# @Software: PyCharm
# @Blog    : https://www.hecady.com
from flask import jsonify, render_template, request, abort, redirect, Blueprint
from app.service.bilibiliCover import BilibiliCover

index_bp = Blueprint("index", __name__, "")


@index_bp.route("/")
def index():
    return render_template("index.html")


@index_bp.route("/page")
def index_page():
    return redirect("https://i.hecady.com")


@index_bp.route("/download")
def download():
    return redirect("https://github.com/Smalltred/BilibiliCover")


@index_bp.route("/apiPage")
def api_page():
    return redirect("http://api.hecady.com")


@index_bp.route("/api", methods=["GET", "POST"])
def bilibiliApi():
    get_data = request.args.to_dict()
    if len(get_data) == 0:
        result = {"code": 404, "msg": "请求不合法"}
        return jsonify(result)
    url = get_data.get("b")
    if 'b' not in get_data or not get_data['b']:
        result = {"code": 404, "msg": "请求不合法"}
        return result
    bilibili = BilibiliCover(url)
    result = bilibili.get_cover()
    return jsonify(result)


@index_bp.route("/", methods=["GET", "POST"])
def handleResult():
    if request.method == "POST":
        data = request.form.get("text")
        bilibili = BilibiliCover(data)
        result = bilibili.get_cover()
        if result is not None:
            if result.get("code") == 200:
                video_data = result.get("data")
                if video_data is not None:
                    # 多个视频
                    if isinstance(video_data, list):
                        return render_template("covers.html", result=video_data)
                    # 单个视频
                    elif isinstance(video_data, dict):
                        # states = 1 上线 states = 0 没上线
                        if video_data.get("states") == 1:
                            # 番剧上线了 有ep 有pv
                            if video_data.get("eps") is not None and video_data.get("pvs") is not None:
                                eps = video_data.get("eps")
                                pvs = video_data.get("pvs")
                                return render_template("mds.html", pvs=pvs, eps=eps, result=video_data)
                            # 番剧上线了 有ep 没有pv
                            else:
                                eps = video_data.get("eps")
                                return render_template("ep.html", eps=eps, result=video_data)
                        # 番剧没上线 只有pv
                        elif video_data.get("states") == 0:
                            pvs = video_data.get("pvs")
                            return render_template("pv.html", pvs=pvs, result=video_data)
                        else:
                            # 视频单p
                            return render_template("cover.html", result=video_data, )
            elif result.get("code") == 403:
                return render_template("error.html", result=result)
            else:
                return abort(404)

        else:
            return render_template("error.html", result={"msg": "获取不到封面哦~"})
