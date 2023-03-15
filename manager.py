#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
# @Time    : 2023/3/14 19:06
# @Author  : Small tred
# @FileName: manager.py
# @Software: PyCharm
# @Blog    : https://www.hecady.com
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from app import create_app

app = create_app()

manager = Manager(app)

if __name__ == '__main__':
    manager.run()
