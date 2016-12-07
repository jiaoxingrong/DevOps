#!/bin/env python
#coding: utf-8

from __future__ import division

def proportion(num_list,pro_num):
    subtotal = sum(num_list)
    for num in num_list:
        total_num_list = sum(num_list)
        print "%.2f" % (pro_num * (num/total_num_list))

num_list = [200,100, 300, 300, 300, 300, 300, 100, 500, 300, 500, 500, 500, 300, 300, 300]
pro_num = 748.14
proportion(num_list,pro_num)
