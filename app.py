#!/usr/bin/python
# -- coding: utf-8 --
# @Author : Small_tred
from flask import Flask, jsonify, render_template, request, abort
from gevent import pywsgi
from bilibiliCover import BilibiliCover
from flask_caching import Cache

app = Flask(__name__)
app.debug = False
app.config["JSON_AS_ASCII"] = False
cache = Cache(app, config={'CACHE_TYPE': 'simple'})


@app.route("/")
@cache.cached(timeout=3600)
def index():
    return render_template("index.html")


@app.route("/api/", methods=["GET", "POST"])
@cache.cached(timeout=3600)
def bilibiliApi():
    if request.args is None:
        error = {"code": 403, "msg": "这好像不是B站的链接哦~"}
        return error
    get_data = request.args.to_dict()
    url = get_data.get("url")
    bilibili = BilibiliCover(url)
    result = bilibili.get_cover()
    print(result)
    return jsonify(result)


@cache.cached(timeout=3600)
@app.route("/", methods=["GET", "POST"])
def handleResult():
    if request.method == "POST":
        data = request.form.get("text")
        bilibili = BilibiliCover(data)
        result = bilibili.get_cover()
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
                        return render_template("cover.html", result=video_data)
        elif result.get("code") == 403:
            return render_template("error.html", result=result)
        else:
            return abort(404)


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 80), app)
    server.serve_forever()
