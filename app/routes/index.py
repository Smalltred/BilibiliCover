#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
# @Time    : 2023/3/14 19:13
# @Author  : Small tred
# @FileName: routes.py
# @Software: PyCharm
# @Blog    : https://www.hecady.com
import threading
from flask import jsonify, render_template, request, abort, redirect, Blueprint
from app.service import BilibiliCover, DataPreprocessor

index_bp = Blueprint("index", __name__, "")


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
def index():
    if request.method != "POST":
        return render_template("index.html")
    data = request.form.get("text")
    result = BilibiliCover(data).get_cover()
    DataPreprocessor(data).process_data()
    if result is None:
        return render_template("error.html", result={"msg": "获取不到封面哦~"})

    code, video_data = result.get("code"), result.get("data")
    if code != 200:
        return abort(404)

    if isinstance(video_data, list):
        return render_template("covers.html", result=video_data)

    states = video_data.get("states")

    if states == 1:
        eps, pvs = video_data.get("eps"), video_data.get("pvs")
        if eps is not None and pvs is not None:
            return render_template("mds.html", pvs=pvs, eps=eps, result=video_data)
        else:
            return render_template("mds.html", eps=eps, result=video_data)

    elif states == 0:
        pvs = video_data.get("pvs")
        return render_template("pv.html", pvs=pvs, result=video_data)

    else:
        return render_template("cover.html", result=video_data)
