#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'Jerome'
__mtime__ = '2017/5/22'

"""
from django.http import HttpResponse
from django.template import Template, Context


def hello(request, number):
    t = Template('<html><body>The number is {{ number }}. </body></html>')
    r = t.render(Context({'number': number}))
    return HttpResponse(r)
