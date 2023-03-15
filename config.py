#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
# @Time    : 2023/3/14 19:19
# @Author  : Small tred
# @FileName: config.py
# @Software: PyCharm
# @Blog    : https://www.hecady.com

class Config:
    JSON_AS_ASCII = False
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:1842244757@127.0.0.1:3306/bilibili'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_POOL_TIMEOUT = 10
    SQLALCHEMY_ECHO = False

