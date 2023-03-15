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
from app.service.bilibiliCover import BilibiliCover


class DataPreprocessor(BilibiliCover):
    ip = None

    def __init__(self, content):
        super().__init__(content)

    def get_client_ip(self):
        if "X-Real-IP" in request.headers:
            ip = request.headers["X-Real-IP"]
        elif "X-Forwarded-For" in request.headers:
            ip = request.headers["X-Forwarded-For"]
        else:
            ip = request.remote_addr
        self.ip = ip
        return ip

    def handle(self):
        tmp = []
        result = self.get_cover()
        if result is not None:
            if self.id_type == "bv":
                if isinstance(result.get("data"), dict):
                    data = result.get("data")
                    data["id_type"] = self.id_type
                    data["ip"] = self.get_client_ip()
                    data = [data]
                    return self._write_by_vdCover(data)
                elif isinstance(result.get("data"), list):
                    data = result.get("data")
                    for item in data:
                        item["id_type"] = self.id_type
                        item["ip"] = self.get_client_ip()
                        tmp.append(item)
                    data = tmp
                    return self._write_by_vdCover(data)
            elif self.id_type == "ss" or self.id_type == "ep":
                data = result.get("data")
                data["id_type"] = self.id_type
                data["ip"] = self.get_client_ip()
                data = [data]
                return self._write_by_vdCover(data)
            elif self.id_type == "md":
                if result.get("data").get("pvs") is not None and result.get("data").get("eps") is None:
                    data = result.get("data")
                    md_title = data.get("title")
                    md_cover = data.get("md_cover")
                    md_url = data.get("md_url")
                    states = data.get("states")
                    pvs_data = data.get("pvs")
                    for pv_item in pvs_data:
                        pv_item["md_title"] = md_title
                        pv_item["md_cover"] = md_cover
                        pv_item["md_url"] = md_url
                        pv_item["states"] = states
                        pv_item["id_type"] = self.id_type
                        pv_item["ip"] = self.get_client_ip()
                        tmp.append(pv_item)
                    return self._write_by_mdCover(data)
                else:
                    tmp = []
                    data = result.get("data")
                    md_title = data.get("md_title")
                    md_cover = data.get("md_cover")
                    md_url = data.get("md_url")
                    states = data.get("states")
                    eps_data = data.get("eps")
                    pvs_data = data.get("pvs")
                    for ep_item in eps_data:
                        ep_item["md_title"] = md_title
                        ep_item["md_cover"] = md_cover
                        ep_item["md_url"] = md_url
                        ep_item["states"] = states
                        ep_item["id_type"] = self.id_type
                        ep_item["ip"] = self.get_client_ip()
                        tmp.append(ep_item)
                    for pv_item in pvs_data:
                        pv_item["md_title"] = md_title
                        pv_item["md_cover"] = md_cover
                        pv_item["md_url"] = md_url
                        pv_item["states"] = states
                        pv_item["id_type"] = self.id_type
                        pv_item["ip"] = self.get_client_ip()
                        tmp.append(pv_item)
                    data = tmp
                    print(data)
                    return self._write_by_mdCover(data)

    @staticmethod
    def _write_by_vdCover(data):
        write = Insert()
        write.commit_by_vdCover(data)
        print("插入成功")

    @staticmethod
    def _write_by_mdCover(data):
        write = Insert()
        write.commit_by_mdCover(data)
        print("插入成功")


class Insert:
    def commit_by_vdCover(self, data: list):
        return self._commit(VdCover, data)

    def commit_by_mdCover(self, data: list):
        return self._commit(MdCovers, data)

    @staticmethod
    def _commit(table, result):
        if issubclass(table, VdCover):
            for item in result:
                db.session.add(table(**item))
            db.session.commit()
        if issubclass(table, MdCovers):
            for item in result:
                db.session.add(table(**item))
            db.session.commit()
