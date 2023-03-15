#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
# @Time    : 2023/3/15 11:24
# @Author  : Small tred
# @FileName: db.py
# @Software: PyCharm
# @Blog    : https://www.hecady.com
from app import db


class VdCover(db.Model):
    __tablename__ = "vd_cover"
    id = db.Column(db.Integer, primary_key=True, comment='ID')
    title = db.Column(db.String(100), unique=False, nullable=False, comment='视频标题')
    bvid = db.Column(db.String(200), unique=False, nullable=False, comment='BV号')
    avid = db.Column(db.String(200), unique=False, nullable=False, comment='AV号')
    image = db.Column(db.String(200), unique=False, nullable=False, comment='封面地址')
    url = db.Column(db.String(200), unique=False, nullable=False, comment='视频地址')
    id_type = db.Column(db.String(200), unique=False, nullable=False, comment='链接类型')
    ip = db.Column(db.String(32), nullable=False, comment='用户IP')


class MdCovers(db.Model):
    __tablename__ = "md_cover"
    id = db.Column(db.Integer, primary_key=True, comment='ID')
    title = db.Column(db.String(100), unique=False, nullable=False, comment='视频标题')
    bvid = db.Column(db.String(200), unique=False, nullable=False, comment='BV号')
    avid = db.Column(db.String(200), unique=False, nullable=False, comment='AV号')
    image = db.Column(db.String(200), unique=False, nullable=False, comment='封面地址')
    url = db.Column(db.String(200), unique=False, nullable=False, comment='视频地址')
    volume = db.Column(db.Integer, unique=False, nullable=True, comment='集数')
    id_type = db.Column(db.String(200), unique=False, nullable=False, comment='链接类型')
    md_title = db.Column(db.String(200), unique=False, nullable=False, comment='md标题')
    md_url = db.Column(db.String(200), unique=False, nullable=False, comment='md链接')
    md_cover = db.Column(db.String(200), unique=False, nullable=False, comment='md封面')
    states = db.Column(db.Integer, unique=False, nullable=False, comment='上线状态')
    ip = db.Column(db.String(32), nullable=False, comment='用户IP')
