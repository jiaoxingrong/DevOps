#!/bin/env python
#coding: utf-8

from __future__ import division

def proportion(num_list,pro_num):
    subtotal = sum(num_list)
    for num in num_list:
        total_num_list = sum(num_list)
        print "%.2f" % (pro_num * (num/total_num_list))

num_list = [530,530,530,530,130,130,530,530,530,130,608,30]
pro_num = 1165.67
proportion(num_list,pro_num)
