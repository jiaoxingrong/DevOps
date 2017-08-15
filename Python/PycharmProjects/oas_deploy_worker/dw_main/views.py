# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

import boto3
import ConfigParser

# Create your views here.

class classa(object):
    def __init__(self, text):
        self.text = text
        
    def func1(self):
        print self.text

def func1():
    print 'a'
    
        
c1 = classa('hello')
c1.func1()