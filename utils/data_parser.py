#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
@author:silenthz 
@file: data_parser.py
@time: 2018/06/06
@报表解析工具库
"""


# 处理及时率示例
def deal_in_time_rate_parser():
    # 解析报表文件为元组,分组,排序
    dict = {'广州': 99, '深圳': 98, '东莞': 97, '佛山': 100, '珠海': 88, '中山': 95, '惠州': 87, '江门': 85}
    sortedTuple = sorted(dict.items(), key=lambda x: x[1], reverse=True)
    cities = []
    rate = []
    for item in sortedTuple:
        cities.append(item[0])
        rate.append(item[1])
    return cities, rate
