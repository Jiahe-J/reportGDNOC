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


#  按年度,季度进行工单量汇总,返回已排序的的{区域:[{城市:工单量}]}字典
def collect_order_amount(year, quarter):
    # 构建dict
    order_amount_dict = {}
    if quarter >= 1 and quarter <= 4:
        begin_datetime = datetime.date(year, quarter, 1)
        end_datetime = datetime.date(year, quarter * 3, calendar.mdays[quarter * 3])

        # => <QuerySet [{'city': '东莞', 'order_amount': 1563}, {'city': '清远', 'order_amount': 2099}, {'city': '韶关', 'order_amount': 1548}, {'city': '珠海', 'order_amount': 1698}, {'city': '江门', 'order_amount': 2444}, {'city': '中山', 'order_amount': 2005}, {'city': '广州', 'order_amount': 8454}]>
        # order_admout_qureyset.filter(city='东莞').get('order_amount')
        order_amount_qureyset = MalfunctionData.objects.filter(distributeTime__gte=begin_datetime, distributeTime__lte=end_datetime).values(
            'city').annotate(order_amount=Count('*'))

        # 珠1地区 Pearl River Delta 1
        prd_1_amount = get_district_order_amount(1, order_amount_qureyset)
        # {'prd_1': [{'city': '广州', 'order_amount': 8454}, {'city': '东莞', 'order_amount': 1563}, {'city': '深圳', 'order_amount': 0}, {'city': '佛山', 'order_amount': 0}]}
        order_amount_dict['prd_1'] = prd_1_amount
        prd_2_amount = get_district_order_amount(2, order_amount_qureyset)
        order_amount_dict['prd_2'] = prd_2_amount
        gd_e_amount = get_district_order_amount(3, order_amount_qureyset)
        order_amount_dict['gd_e'] = gd_e_amount
        gd_w_amount = get_district_order_amount(4, order_amount_qureyset)
        order_amount_dict['gd_w'] = gd_w_amount
        gd_n_amount = get_district_order_amount(5, order_amount_qureyset)
        order_amount_dict['gd_n'] = gd_n_amount
        order_amount_dict['status'] = 'success'
    else:
        order_amount_dict['status'] = 'fail'
    return order_amount_dict


# 根据区域ID,order_admout_qureyset返回排序好的区域字典列表
# 珠1:1,珠2:2,粤东:3,粤西:4,粤北:5
def get_district_order_amount(district_id, order_amount_qureyset):
    cities = get_cities_by_district_id(district_id)
    order_amount = []
    for i in cities:
        amount_item = dict()
        amount_item['city'] = i
        qs = order_amount_qureyset.filter(city=i)
        if qs:
            amount_item['order_amount'] = qs[0].get('order_amount')
        else:
            amount_item['order_amount'] = 0
        order_amount.append(amount_item)
    district_order_amount = sorted(order_amount, key=operator.itemgetter('order_amount'), reverse=True)
    return district_order_amount


# 根据地区id获取城市列表
def get_cities_by_district_id(district_id):
    districtCity = DistrictCity.objects.filter(district=district_id)
    city_ids = []
    for i in districtCity:
        city_ids.append(i.city_id)
    cities = []
    for i in City.objects.filter(id__in=city_ids):
        cities.append(i.city)
    return cities


#  按年度,季度进行工单处理及时率汇总,返回已排序的{区域:[{城市:工单处理及时率}]}字典
def collect_deal_in_time_rate(year, quarter):
    # 构建dict
    deal_in_time_rate_dict = {}
    if quarter >= 1 and quarter <= 4:
        begin_datetime = datetime.date(year, quarter, 1)
        end_datetime = datetime.date(year, quarter * 3, calendar.mdays[quarter * 3])
        # <QuerySet [{'city': '东莞', 'isTimeOut': '否', 'istimeut_amount': 1512}, {'city': '韶关', 'isTimeOut': '否', 'istimeut_amount': 1433}, {'city': '珠海', 'isTimeOut': '否', 'istimeut_amount': 1554}, {'city': '江门', 'isTimeOut': '否', 'istimeut_amount': 2345}, {'city': '中山', 'isTimeOut': '否', 'istimeut_amount': 1986}, {'city': '清远', 'isTimeOut': '否', 'istimeut_amount': 2001}, {'city': '广州', 'isTimeOut': '否', 'istimeut_amount': 8198}]>
        deal_in_time_qureyset = MalfunctionData.objects.filter(distributeTime__gte=begin_datetime, distributeTime__lte=end_datetime).values(
            'city', 'isTimeOut').annotate(deal_in_time_amount=Count('isTimeOut')).filter(isTimeOut='否')
        order_amount_qureyset = MalfunctionData.objects.filter(distributeTime__gte=begin_datetime, distributeTime__lte=end_datetime).values(
            'city').annotate(order_amount=Count('city'))
        prd_1_rate = get_district_deal_in_time_rate(1, deal_in_time_qureyset, order_amount_qureyset)
        deal_in_time_rate_dict['prd_1'] = prd_1_rate
        prd_2_rate = get_district_deal_in_time_rate(2, deal_in_time_qureyset, order_amount_qureyset)
        deal_in_time_rate_dict['prd_2'] = prd_2_rate
        gd_e_rate = get_district_deal_in_time_rate(3, deal_in_time_qureyset, order_amount_qureyset)
        deal_in_time_rate_dict['gd_e'] = gd_e_rate
        gd_w_rate = get_district_deal_in_time_rate(4, deal_in_time_qureyset, order_amount_qureyset)
        deal_in_time_rate_dict['gd_w'] = gd_w_rate
        gd_n_rate = get_district_deal_in_time_rate(5, deal_in_time_qureyset, order_amount_qureyset)
        deal_in_time_rate_dict['gd_n'] = gd_n_rate
        deal_in_time_rate_dict['status'] = 'success'
    else:
        deal_in_time_rate_dict['status'] = 'fail'
    return deal_in_time_rate_dict


# 根据区域ID,order_deal_in_time_qureyset返回排序好的区域字典列表
# 珠1:1,珠2:2,粤东:3,粤西:4,粤北:5
def get_district_deal_in_time_rate(distirct_id, deal_in_time_qureyset, order_amount_qureyset):
    cities = get_cities_by_district_id(distirct_id)
    deal_in_time_rate_list = []

    for i in cities:
        deal_in_time_rate_item = dict()
        deal_in_time_rate_item['city'] = i
        qs = order_amount_qureyset.filter(city=i)
        if qs:
            order_amount = qs[0].get('order_amount')
        else:
            order_amount = 1
        qs1 = deal_in_time_qureyset.filter(city=i)
        if qs1:
            deal_in_time_amount = qs1[0].get('deal_in_time_amount')
        else:
            deal_in_time_amount = 0
        deal_in_time_rate_item['deal_in_time_rate'] = round(deal_in_time_amount / order_amount * 100, 2)
        deal_in_time_rate_list.append(deal_in_time_rate_item)
    district_deal_in_time_rate = sorted(deal_in_time_rate_list, key=operator.itemgetter('deal_in_time_rate'), reverse=True)
    return district_deal_in_time_rate
