#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
@author:silenthz 
@file: data_collect.py 
@time: 2018/06/18 
"""
import calendar
import datetime
import operator

from django.db.models import Count

from report.models import MalfunctionData, District, City, DistrictCity


#  按年度,季度进行工单量汇总,返回以区域划分的工单量字典
def collect_order_amount(year, quarter):
    if quarter >= 1 and quarter <= 4:
        begin_datetime = datetime.date(year, quarter, 1)
        end_datetime = datetime.date(year, quarter * 3, calendar.mdays[quarter * 3])

        # => <QuerySet [{'city': '东莞', 'order_amount': 1563}, {'city': '清远', 'order_amount': 2099}, {'city': '韶关', 'order_amount': 1548}, {'city': '珠海', 'order_amount': 1698}, {'city': '江门', 'order_amount': 2444}, {'city': '中山', 'order_amount': 2005}, {'city': '广州', 'order_amount': 8454}]>
        # order_admout_qureyset.filter(city='东莞').get('order_amount')
        order_admout_qureyset = MalfunctionData.objects.filter(distributeTime__gte=begin_datetime, distributeTime__lte=end_datetime).values(
            'city').annotate(order_amount=Count('city'))
        # 构建dict
        order_amount_dict = {}
        # 珠1地区 Pearl River Delta 1
        prd_1_amount = get_district_order_amount(1, order_admout_qureyset)
        # {'prd_1': [{'city': '广州', 'order_amount': 8454}, {'city': '东莞', 'order_amount': 1563}, {'city': '深圳', 'order_amount': 0}, {'city': '佛山', 'order_amount': 0}]}
        order_amount_dict['prd_1'] = prd_1_amount
        prd_2_amount = get_district_order_amount(2, order_admout_qureyset)
        order_amount_dict['prd_2'] = prd_2_amount
        gd_e_amount = get_district_order_amount(3, order_admout_qureyset)
        order_amount_dict['gd_e'] = gd_e_amount
        gd_w_amount = get_district_order_amount(4, order_admout_qureyset)
        order_amount_dict['gd_w'] = gd_w_amount
        gd_n_amount = get_district_order_amount(5, order_admout_qureyset)
        order_amount_dict['gd_n'] = gd_n_amount
        return order_amount_dict


# 根据区域ID,order_admout_qureyset返回排序好的区域字典列表
# 珠1:1,珠2:2,粤东:3,粤西:4,粤北:5
def get_district_order_amount(id, order_admout_qureyset):
    districtCity = DistrictCity.objects.filter(district=id)
    city_ids = []
    for i in districtCity:
        city_ids.append(i.city_id)
    cities = []
    for i in City.objects.filter(id__in=city_ids):
        cities.append(i.city)
    order_amount = []
    for i in cities:
        amount_item = dict()
        amount_item['city'] = i
        if order_admout_qureyset.filter(city=i):
            amount_item['order_amount'] = order_admout_qureyset.filter(city=i)[0].get('order_amount')
        else:
            amount_item['order_amount'] = 0
        order_amount.append(amount_item)
    district_order_amount = sorted(order_amount, key=operator.itemgetter('order_amount'), reverse=True)
    return district_order_amount
