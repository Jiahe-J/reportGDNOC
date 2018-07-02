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

from report.models import MalfunctionData, City, DistrictCity, StatisticsAmount, StatisticsInTimeRate


#  按年度,季度进行工单量汇总,返回已排序的的{区域:[{城市:工单量}]}字典
def collect_order_amount(year, quarter):
    # 构建dict
    order_amount_dict = {}
    sum_amount = 0
    if quarter >= 1 and quarter <= 4:
        begin_datetime = datetime.date(year, quarter, 1)
        end_datetime = datetime.date(year, quarter * 3, calendar.mdays[quarter * 3])
        # 如统计表中无数据则根据工单数据表进行统计:
        if not StatisticsAmount.objects.filter(yearNum=year, quarterNum=quarter):
            order_amount_qureyset = MalfunctionData.objects.filter(distributeTime__gte=begin_datetime, distributeTime__lte=end_datetime).values(
                'city', 'profession').annotate(order_amount=Count('*'))
            statistics_amount_list = []
            for q in order_amount_qureyset:
                if q.get("city"):
                    statistics_amount = StatisticsAmount()
                    statistics_amount.yearNum = year
                    statistics_amount.quarterNum = quarter
                    statistics_amount.statisticsType = 2
                    statistics_amount.city = q.get("city")
                    statistics_amount.profession = q.get('profession')
                    statistics_amount.result = q.get("order_amount")
                    statistics_amount_list.append(statistics_amount)
            StatisticsAmount.objects.bulk_create(statistics_amount_list)

            profession_list = ["传输", '动力', '交换', '接入网', '无线']
            for p in profession_list:
                statistics_amount = StatisticsAmount()
                statistics_amount.yearNum = year
                statistics_amount.quarterNum = quarter
                statistics_amount.statisticsType = 2
                statistics_amount.city = '广东'
                statistics_amount.profession = p
                result = MalfunctionData.objects.filter(profession=p, distributeTime__gte=begin_datetime, distributeTime__lte=end_datetime).count()
                statistics_amount.result = result
                sum_amount += result
                statistics_amount.save()

        # 珠1地区 Pearl River Delta 1
        prd_1_amount = get_district_order_amount(1, year, quarter)
        order_amount_dict['prd_1'] = prd_1_amount
        prd_2_amount = get_district_order_amount(2, year, quarter)
        order_amount_dict['prd_2'] = prd_2_amount
        gd_e_amount = get_district_order_amount(3, year, quarter)
        order_amount_dict['gd_e'] = gd_e_amount
        gd_w_amount = get_district_order_amount(4, year, quarter)
        order_amount_dict['gd_w'] = gd_w_amount
        gd_n_amount = get_district_order_amount(5, year, quarter)
        order_amount_dict['gd_n'] = gd_n_amount

        qs = StatisticsAmount.objects.filter(yearNum=year, quarterNum=quarter, city='广东')
        profession_amount_list = []
        for i in qs:
            if i.profession != "WIFI":
                profession_amount = dict()
                profession_amount['profession'] = i.profession
                profession_amount['amount'] = i.result
                sum_amount += i.result
                profession_amount_list.append(profession_amount)
            # 未含WiFi专业的工单总量
        order_amount_dict['gd'] = dict()
        order_amount_dict['gd']['profession_amount'] = profession_amount_list
        order_amount_dict['gd']['sum_amount'] = sum_amount
        order_amount_dict['status'] = 'success'

    else:
        order_amount_dict['status'] = 'fail'

    return order_amount_dict


# 根据区域ID,order_admout_qureyset返回排序好的区域字典列表
# 珠1:1,珠2:2,粤东:3,粤西:4,粤北:5
def get_district_order_amount(district_id, year, quarter):
    cities = get_cities_by_district_id(district_id)
    order_amount = []
    for i in cities:
        amount_item = dict()
        amount_item['city'] = i
        result_list = StatisticsAmount.objects.filter(city=i, yearNum=year, quarterNum=quarter)
        if result_list:
            sum_amount = 0
            profession_amount_list = []
            for i in result_list:
                profession_amount = dict()
                profession_amount['profession'] = i.profession
                profession_amount['amount'] = i.result
                if profession_amount['amount'] != "WiFi":
                    sum_amount += i.result
                profession_amount_list.append(profession_amount)
            # 未含WiFi专业的工单总量
            amount_item['sum_amount'] = sum_amount
            amount_item['profession_amount'] = profession_amount_list
            order_amount.append(amount_item)
    district_order_amount = sorted(order_amount, key=operator.itemgetter('sum_amount'), reverse=True)
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
        if not StatisticsInTimeRate.objects.filter(yearNum=year, quarterNum=quarter):
            begin_datetime = datetime.date(year, quarter, 1)
            end_datetime = datetime.date(year, quarter * 3, calendar.mdays[quarter * 3])
            deal_in_time_qureyset = MalfunctionData.objects.filter(distributeTime__gte=begin_datetime, distributeTime__lte=end_datetime).values(
                'city', 'isTimeOut').annotate(deal_in_time_amount=Count('isTimeOut')).filter(isTimeOut='否')
            order_amount_qureyset = MalfunctionData.objects.filter(distributeTime__gte=begin_datetime, distributeTime__lte=end_datetime).values(
                'city').annotate(order_amount=Count('*'))
            rate_item_list = []
            for i in deal_in_time_qureyset:
                city = i.get('city')
                if city:
                    rate_item = StatisticsInTimeRate()
                    rate_item.yearNum = year
                    rate_item.quarterNum = quarter
                    rate_item.statisticsType = 2
                    rate_item.city = city
                    order_amount = order_amount_qureyset.get(city=city).get('order_amount')
                    order_amount = order_amount if order_amount else 1
                    in_time_rate_amount = i.get('deal_in_time_amount')
                    in_time_rate_amount = in_time_rate_amount if in_time_rate_amount else 0
                    rate_item.result = round(in_time_rate_amount / order_amount * 100, 2)
                    rate_item_list.append(rate_item)
            StatisticsInTimeRate.objects.bulk_create(rate_item_list)

        prd_1_rate = get_district_deal_in_time_rate(1, year, quarter)
        deal_in_time_rate_dict['prd_1'] = prd_1_rate
        prd_2_rate = get_district_deal_in_time_rate(2, year, quarter)
        deal_in_time_rate_dict['prd_2'] = prd_2_rate
        gd_e_rate = get_district_deal_in_time_rate(3, year, quarter)
        deal_in_time_rate_dict['gd_e'] = gd_e_rate
        gd_w_rate = get_district_deal_in_time_rate(4, year, quarter)
        deal_in_time_rate_dict['gd_w'] = gd_w_rate
        gd_n_rate = get_district_deal_in_time_rate(5, year, quarter)
        deal_in_time_rate_dict['gd_n'] = gd_n_rate
        deal_in_time_rate_dict['status'] = 'success'
    else:
        deal_in_time_rate_dict['status'] = 'fail'
    return deal_in_time_rate_dict


# 根据区域ID,order_deal_in_time_qureyset返回排序好的区域字典列表
# 珠1:1,珠2:2,粤东:3,粤西:4,粤北:5
def get_district_deal_in_time_rate(distirct_id, year, quarter):
    cities = get_cities_by_district_id(distirct_id)
    deal_in_time_rate_list = []

    for i in cities:
        deal_in_time_rate_item = dict()
        deal_in_time_rate_item['city'] = i
        qs = StatisticsInTimeRate.objects.filter(city=i, yearNum=year, quarterNum=quarter)
        if qs:
            deal_in_time_rate_item['deal_in_time_rate'] = qs[0].result
            deal_in_time_rate_list.append(deal_in_time_rate_item)
    district_deal_in_time_rate = sorted(deal_in_time_rate_list, key=operator.itemgetter('deal_in_time_rate'), reverse=True)
    return district_deal_in_time_rate
