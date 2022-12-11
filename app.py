#!/usr/bin/python
# -- coding: utf-8 --
# @Author : Small_tred
from flask import Flask, jsonify, render_template, request, abort
from gevent import pywsgi
from bilibiliCover import BilibiliCover

app = Flask(__name__)
app.debug = False
app.config["JSON_AS_ASCII"] = False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/<path:string>", methods=["GET", "POST"])
def bilibiliApi(string):
    bilibili = BilibiliCover(string)
    result = bilibili.get_cover()
    return jsonify(result)


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
                        if video_data.get("ep") is not None and video_data.get("pv") is not None:
                            eps = result.get("ep")
                            pvs = result.get("pv")
                            return render_template("mds.html", pvs=pvs, eps=eps, result=video_data)
                        # 番剧上线了 有ep 没有pv
                        else:
                            eps = result.get("ep")
                            return render_template("ep.html", eps=eps, result=video_data)
                    # 番剧没上线 只有pv
                    elif video_data.get("states") == 0:
                        pvs = result.get("pv")
                        return render_template("pv.html", pvs=pvs, result=video_data)
                    else:
                        # 视频单p
                        return render_template("cover.html", result=video_data)
        elif result.get("code") == 403:
            return jsonify(result)
        else:
            return abort(404)


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 80), app)
    server.serve_forever()
