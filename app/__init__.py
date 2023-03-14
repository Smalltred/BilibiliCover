#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
# @Time    : 2023/3/14 19:06
# @Author  : Small tred
# @FileName: __init__.py
# @Software: PyCharm
# @Blog    : https://www.hecady.com
from flask import Flask
from config import Config


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)

    # 加载蓝图
    from app.routes.index import index_bp
    app.register_blueprint(index_bp)
    return app