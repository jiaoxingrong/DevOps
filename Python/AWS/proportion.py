#!/bin/env python
#coding: utf-8

from __future__ import division

def proportion(num_list,pro_num):
    subtotal = sum(num_list)
    for num in num_list:
        total_num_list = sum(num_list)
        print "%.2f" % (pro_num * (num/total_num_list))

num_list = [200,500,1500,900,100,200,300,1500,300,200]
pro_num = 811.01
proportion(num_list,pro_num)
