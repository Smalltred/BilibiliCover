#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
# @Time    : 2023/3/15 11:58
# @Author  : Small tred
# @FileName: db_operate.py.py
# @Software: PyCharm
# @Blog    : https://www.hecady.com
from flask import request
from app.models.db import VdCover, MdCovers
from app import db
from .bilibiliCover import BilibiliCover


class DataPreprocessor(BilibiliCover):
    def __init__(self, content):
        super().__init__(content)

    @staticmethod
    def get_client_ip():
        headers = request.headers
        ip = headers.get('X-Real-IP') or headers.get('X-Forwarded-For') or request.remote_addr
        return ip

    def process_data(self):
        insert = Insert()
        ip = self.get_client_ip()
        tmp = []
        result = self.get_cover()
        if not result:
            return
        data = result.get('data')
        if not data:
            return
        id_type = self.id_type
        if id_type == 'bv':
            if isinstance(data, dict):
                data = [data]
            tmp = [{'id_type': id_type, 'ip': ip, **item} for item in data]
            insert.commit_by_cover_type("vdCover", tmp)
        elif id_type in {'ss', 'ep'}:
            tmp = [{'id_type': id_type, 'ip': ip, **data}]
            insert.commit_by_cover_type("vdCover", tmp)
        elif id_type == 'md':
            md_title, md_cover, md_url = data.get('md_title'), data.get('md_cover'), data.get('md_url')
            states, eps_data, pvs_data = data.get('states'), data.get('eps'), data.get('pvs')
            if not pvs_data and eps_data:
                for item in eps_data:
                    tmp.append({'md_title': md_title, 'md_cover': md_cover, 'md_url': md_url,
                                'states': states, 'id_type': id_type, 'ip': ip, **item})
                insert.commit_by_cover_type("mdCover", tmp)
            if pvs_data and eps_data:
                for item in pvs_data:
                    tmp.append({'md_title': md_title, 'md_cover': md_cover, 'md_url': md_url,
                                'states': states, 'id_type': id_type, 'ip': ip, **item})
                for item in eps_data:
                    tmp.append({'md_title': md_title, 'md_cover': md_cover, 'md_url': md_url,
                                'states': states, 'id_type': id_type, 'ip': ip, **item})
                insert.commit_by_cover_type("mdCover", tmp)


class Insert:

    @staticmethod
    def commit(table, data):
        with db.session.begin(subtransactions=True):
            for item in data:
                db.session.add(table(**item))

    def commit_by_cover_type(self, cover_type, data):
        if cover_type == 'vdCover':
            self.commit(VdCover, data)
        elif cover_type == 'mdCover':
            self.commit(MdCovers, data)
        else:
            raise ValueError('Invalid cover type')

        print('插入成功')
