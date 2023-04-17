#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
# @Time    : 2023/3/14 19:13
# @Author  : Small tred
# @FileName: routes.py
# @Software: PyCharm
# @Blog    : https://www.hecady.com
import time

from flask import request, Blueprint, jsonify
from app.service import BilibiliCover
from app import cache

obj = BilibiliCover

api = Blueprint("api", __name__)


@api.after_request
def cors(environ):
    environ.headers['Access-Control-Allow-Origin'] = '*'
    environ.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    environ.headers["Access-Control-Allow-Headers"] = "x-requested-with,content-type"
    return environ


def make_cache_key(*args, **kwargs):
    """Dynamic creation the request url."""

    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return (path + args).encode('utf-8')


@api.route("/", methods=["GET", "POST"])
@cache.cached(timeout=60 * 60 * 24, key_prefix=make_cache_key)
def index():
    data = request.args.get("url")
    if data == "":
        return jsonify({"code": -404, "message": "你又调皮了"})
    result = obj(data).cover()
    if result.get("code") not in {-404, -400, -1}:
        return jsonify({"code": 200, "message": "获取成功", "data": result})
    else:
        return jsonify(result)
