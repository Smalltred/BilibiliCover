#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
# @Time    : 2023/3/14 19:06
# @Author  : Small tred
# @FileName: __init__.py
# @Software: PyCharm
# @Blog    : https://www.hecady.com
from flask import Flask
from config import Config
from flask_caching import Cache

cache = Cache()


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)

    # 加载缓存
    cache.init_app(app)

    # 加载蓝图
    from app.routes import api, index
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(index, url_prefix='/')
    return app
