#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'Jerome'
__mtime__ = '16/4/29'
# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
             ┏┓   ┏┓
            ┏┛┻━━━┛┻┓
            ┃    ☃   ┃
            ┃ ┳┛  ┗┳┃
            ┃    ┻  ┃
            ┗━┓   ┏━┛
              ┃   ┗━━━┓
              ┃ 神兽保佑 ┣┓
              ┃ 永无BUG ! ┏┛
              ┗┓┓┏━┳┓┏┛
               ┃┫┫ ┃┫┫
               ┗┻┛ ┗┻┛
"""
from flask import Flask
from werkzeug.security import generate_password_hash,check_password_hash
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()
engine = db.create_engine('mysql://root:123456@localhost:3306/account')
metadata = db.Metadata()
account = db.Table(
    'user',
    metadata,
    db.Column('id', db.INTEGER, primary_key=True),
    db.Column('user', db.VARCHAR(20)),
    db.Column('pass')
) 
