#!/usr/bin/python
# -- coding: utf-8 --
# @Author : Small_tred 
# @Time : 2022/3/24 0:06
from flask import Flask, jsonify, url_for, redirect, render_template, request
from gevent import pywsgi
from bilibiliCover import main

app = Flask(__name__)
app.debug = True
app.config["JSON_AS_ASCII"] = False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/<path:data>")
def bilibiliApi(data):
    result = main(data)
    if result is None:
        return "失败了哦。请检查输入的是否正确"
    else:
        return jsonify(result)


@app.route("/bilibili", methods=["GET", "POST"])
def handleResult():
    if request.method == "POST":
        data = request.form.get("text")
        if data != "":
            result = main(data)
            # 视频多P
            if isinstance(result, list):
                return render_template("covers.html", result=result)
            elif isinstance(result, dict):
                # states = 1 上线 states = 0 没上线
                if result.get("states") == 1:
                    # 番剧上线了 有ep 有pv
                    if result.get("ep") is not None and result.get("pv") is not None:
                        eps = result.get("ep")
                        pvs = result.get("pv")
                        return render_template("mds.html", pvs=pvs, eps=eps, result=result)
                    # 番剧上线了 有ep 没有pv
                    else:
                        eps = result.get("ep")
                        return render_template("ep.html", eps=eps, result=result)
                # 番剧没上线 只有pv
                elif result.get("states") == 0:
                    pvs = result.get("pv")
                    return render_template("pv.html", pvs=pvs, result=result)
                else:
                    return render_template("cover.html", result=result)
            else:
                error = "请检查是否输错了呀, 注意：没上线的番 用ss链接无法获取哦"
                return render_template("error.html", result=error)
        else:
            error = "请检查是否输错了呀, 注意：没上线的番 用ss链接无法获取哦"
            return render_template("error.html", result=error)
    else:
        return redirect(url_for("index"))


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 80), app)
    server.serve_forever()
