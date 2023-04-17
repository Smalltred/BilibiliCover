#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
# @Time    : 2023/4/17 7:59
# @Author  : Small tred
# @FileName: index.py
# @Software: PyCharm
# @Blog    : https://www.hecady.com
from flask import Blueprint, request, jsonify

index = Blueprint("index", __name__)


@index.route("/", methods=["GET"])
def home():
    return "Hello World"
