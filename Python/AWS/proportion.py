#!/bin/env python
#coding: utf-8

from __future__ import division

def proportion(num_list,pro_num):
    subtotal = sum(num_list)
    for num in num_list:
        total_num_list = sum(num_list)
        print "%.2f" % (pro_num * (num/total_num_list))

num_list = [30,30, 1054, 130, 408, 230, 530, 600, 530]
pro_num = 377.9
proportion(num_list,pro_num)
