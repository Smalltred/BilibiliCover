#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
# @Time    : 2023/3/14 19:06
# @Author  : Small tred
# @FileName: manager.py
# @Software: PyCharm
# @Blog    : https://www.hecady.com
from flask_script import Manager
from app import create_app
from app import db

app = create_app()

manager = Manager(app)


@manager.command
def init_db():
    with app.app_context():
        db.create_all()


if __name__ == '__main__':
    manager.run()
