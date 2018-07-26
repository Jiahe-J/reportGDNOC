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

from django.db.models import Count, Avg

from report.models import MalfunctionData, City, DistrictCity, StatisticsAmount, StatisticsInTimeRate, StatisticsDealTime, StatisticsOver48Rate, \
    District


def collect_order_amount(year, quarter):
    if 1 <= quarter <= 4:
        sum_amount = 0
        begin_datetime = datetime.date(year, quarter, 1)
        end_datetime = datetime.date(year, quarter * 3, calendar.mdays[quarter * 3])
        # 如统计表中无数据则根据工单数据表进行统计:
        if not StatisticsAmount.objects.filter(yearNum=year, quarterNum=quarter):
            order_amount_qureyset = MalfunctionData.objects.filter(distributeTime__gte=begin_datetime, distributeTime__lte=end_datetime).values(
                'city', 'profession').annotate(order_amount=Count('*'))
            statistics_amount_list = []
            if order_amount_qureyset:
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
            else:
                return "数据库中无相关数据"

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
            return None
    else:
        return "请求参数有误"


def collect_order_amount_table(year, quarter):
    # 构建dict
    order_amount_dict = {}
    # 构建list
    order_amount_list = []
    try:
        msg = collect_order_amount(year, quarter)
        if msg:
            return {'msg': msg, 'status': 'fail'}
        # 珠1地区 Pearl River Delta 1
        prd_1_amount = get_district_order_amount(1, year, quarter)
        order_amount_list += prd_1_amount
        prd_2_amount = get_district_order_amount(2, year, quarter)
        order_amount_list += prd_2_amount
        gd_e_amount = get_district_order_amount(3, year, quarter)
        order_amount_list += gd_e_amount
        gd_w_amount = get_district_order_amount(4, year, quarter)
        order_amount_list += gd_w_amount
        gd_n_amount = get_district_order_amount(5, year, quarter)
        order_amount_list += gd_n_amount
        order_amount_dict['result'] = order_amount_list
        order_amount_dict['status'] = 'success'
        return order_amount_dict
    except Exception as e:
        order_amount_dict['status'] = 'fail'
        order_amount_dict['msg'] = str(e)
        return order_amount_dict


def collect_order_amount_chart(year, quarter):
    # 构建dict
    order_amount_dict = {}
    try:
        tb_data = collect_order_amount_table(year, quarter)
        if tb_data.get('msg'):
            tb_data['status'] = 'fail'
            return tb_data
        tb_data = tb_data.get('result')
        order_amount_dict['status'] = 'success'
        order_amount_dict['result'] = {}
        cities = []
        transmission = []
        dynamics = []
        exchange = []
        AN = []
        wireless = []
        professions = ['transmission', 'dynamics', 'exchange', 'AN', 'wireless']
        for row in tb_data:
            city = row.get('city')
            cities.append(city)
            for profession in professions:
                data = row.get(profession)
                if profession == 'transmission':
                    transmission.append(data)
                if profession == 'dynamics':
                    dynamics.append(data)
                if profession == 'exchange':
                    exchange.append(data)
                if profession == 'AN':
                    AN.append(data)
                if profession == 'wireless':
                    wireless.append(data)
        order_amount_dict['result']['city'] = cities
        order_amount_dict['result']['transmission'] = transmission
        order_amount_dict['result']['dynamics'] = dynamics
        order_amount_dict['result']['exchange'] = exchange
        order_amount_dict['result']['AN'] = AN
        order_amount_dict['result']['wireless'] = wireless
        return order_amount_dict
    except Exception as e:
        order_amount_dict['status'] = 'fail'
        order_amount_dict['msg'] = str(e)


# 根据区域ID,order_admout_qureyset返回排序好的区域字典列表
# 珠1:1,珠2:2,粤东:3,粤西:4,粤北:5
def get_district_order_amount(district_id, year, quarter):
    area = District.objects.get(id=district_id).district
    cities = get_cities_by_district_id(district_id)
    order_amount = []
    for i in cities:
        amount_item = dict()
        amount_item['area'] = area
        amount_item['city'] = i
        result_list = StatisticsAmount.objects.filter(city=i, yearNum=year, quarterNum=quarter)
        if result_list:
            transmission = result_list.get(profession="传输").result
            dynamics = result_list.get(profession="动力").result
            exchange = result_list.get(profession="交换").result
            AN = result_list.get(profession="接入网").result
            wireless = result_list.get(profession="无线").result
            sum_amount = transmission + dynamics + exchange + AN + wireless
            amount_item['transmission'] = transmission
            amount_item['dynamics'] = dynamics
            amount_item['exchange'] = exchange
            amount_item['AN'] = AN
            amount_item['wireless'] = wireless
            amount_item['sum'] = sum_amount
            order_amount.append(amount_item)
    district_order_amount = sorted(order_amount, key=operator.itemgetter('sum'), reverse=True)
    ls = ['transmission', 'dynamics', 'exchange', 'AN', 'wireless']
    for i in district_order_amount:
        for p in ls:
            i[p] = str(i.get(p))
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
    deal_in_time_rate_list = []
    if quarter >= 1 and quarter <= 4:
        if not StatisticsInTimeRate.objects.filter(yearNum=year, quarterNum=quarter):
            begin_datetime = datetime.date(year, quarter, 1)
            end_datetime = datetime.date(year, quarter * 3, calendar.mdays[quarter * 3])
            deal_in_time_qureyset = MalfunctionData.objects.filter(distributeTime__gte=begin_datetime, distributeTime__lte=end_datetime).values(
                'city', 'isTimeOut').annotate(deal_in_time_amount=Count('isTimeOut')).filter(isTimeOut='否')
            order_amount_qureyset = MalfunctionData.objects.filter(distributeTime__gte=begin_datetime, distributeTime__lte=end_datetime).values(
                'city').annotate(order_amount=Count('*'))
            rate_item_list = []
            if deal_in_time_qureyset and order_amount_qureyset:
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
            else:
                deal_in_time_rate_dict['msg'] = "数据库中无相关数据"
                deal_in_time_rate_dict['status'] = 'fail'
                return deal_in_time_rate_dict

        # 根据区域ID,order_deal_in_time_qureyset返回排序好的区域字典列表
        # 珠1:1,珠2:2,粤东:3,粤西:4,粤北:5
        prd_1_rate = get_district_deal_in_time_rate(1, year, quarter)
        deal_in_time_rate_list.append(prd_1_rate)
        prd_2_rate = get_district_deal_in_time_rate(2, year, quarter)
        deal_in_time_rate_list.append(prd_2_rate)
        gd_e_rate = get_district_deal_in_time_rate(3, year, quarter)
        deal_in_time_rate_list.append(gd_e_rate)
        gd_w_rate = get_district_deal_in_time_rate(4, year, quarter)
        deal_in_time_rate_list.append(gd_w_rate)
        gd_n_rate = get_district_deal_in_time_rate(5, year, quarter)
        deal_in_time_rate_list.append(gd_n_rate)
        deal_in_time_rate_dict['result'] = deal_in_time_rate_list
        deal_in_time_rate_dict['status'] = 'success'
    else:
        deal_in_time_rate_dict['status'] = 'fail'
        deal_in_time_rate_dict['msg'] = '请求参数有误'
    return deal_in_time_rate_dict


def get_district_deal_in_time_rate(district_id, year, quarter):
    area = District.objects.get(id=district_id).district
    cities = get_cities_by_district_id(district_id)
    deal_in_time_rate_list = []

    for i in cities:
        deal_in_time_rate_item = dict()
        deal_in_time_rate_item['area'] = area
        deal_in_time_rate_item['city'] = i
        qs = StatisticsInTimeRate.objects.filter(city=i, yearNum=year, quarterNum=quarter)
        if qs:
            deal_in_time_rate_item['IntimeRate'] = qs[0].result
            deal_in_time_rate_list.append(deal_in_time_rate_item)
    district_deal_in_time_rate = sorted(deal_in_time_rate_list, key=operator.itemgetter('IntimeRate'), reverse=True)
    for i in district_deal_in_time_rate:
        i['IntimeRate'] = str(i.get('IntimeRate'))
    return district_deal_in_time_rate


# 故障平均处理时长统计,按年度,季度进行工单处理及时率汇总
def collect_deal_time(year, quarter):
    deal_time_dict = {}
    deal_time_list = []
    if 1 <= quarter <= 4:
        if not StatisticsDealTime.objects.filter(yearNum=year, quarterNum=quarter):
            begin_datetime = datetime.date(year, quarter, 1)
            end_datetime = datetime.date(year, quarter * 3, calendar.mdays[quarter * 3])
            deal_time_qureyset = MalfunctionData.objects.filter(distributeTime__gte=begin_datetime, distributeTime__lte=end_datetime).values(
                'city').annotate(average_time=Avg('processTime'))
            process_time_list = []
            if deal_time_qureyset:
                for i in deal_time_qureyset:
                    city = i.get('city')
                    if city:
                        process_item = StatisticsDealTime()
                        process_item.yearNum = year
                        process_item.quarterNum = quarter
                        process_item.city = city
                        process_item.statisticsType = 2
                        process_item.result = round(i.get('average_time') / 60, 2)
                        process_time_list.append(process_item)
                StatisticsDealTime.objects.bulk_create(process_time_list)
            else:
                deal_time_dict['msg'] = '数据库中无相关数据'
                deal_time_dict['status'] = 'fail'
                return deal_time_dict
        prd_1_rate = get_district_deal_time(1, year, quarter)
        deal_time_list += prd_1_rate
        prd_2_rate = get_district_deal_time(2, year, quarter)
        deal_time_list += prd_2_rate
        gd_e_rate = get_district_deal_time(3, year, quarter)
        deal_time_list += gd_e_rate
        gd_w_rate = get_district_deal_time(4, year, quarter)
        deal_time_list += gd_w_rate
        gd_n_rate = get_district_deal_time(5, year, quarter)
        deal_time_list += gd_n_rate
        deal_time_dict['result'] = deal_time_list
        deal_time_dict['status'] = 'success'
    else:
        deal_time_dict['status'] = 'fail'
        deal_time_dict['msg'] = '请求参数有误'
    return deal_time_dict


def get_district_deal_time(district_id, year, quarter):
    area = District.objects.get(id=district_id).district
    cities = get_cities_by_district_id(district_id)
    deal_time_list = []

    for i in cities:
        deal_time_item = dict()
        deal_time_item['area'] = area
        deal_time_item['city'] = i
        qs = StatisticsDealTime.objects.filter(city=i, yearNum=year, quarterNum=quarter)
        if qs:
            deal_time_item['AverageTime'] = qs[0].result
            deal_time_list.append(deal_time_item)
    district_deal_time = sorted(deal_time_list, key=operator.itemgetter('AverageTime'), reverse=True)
    for i in district_deal_time:
        i['AverageTime'] = str(i.get('AverageTime'))
    return district_deal_time


#  按年度,季度进行超48小时工单占比统计
def collect_over_48h_rate(year, quarter):
    # 构建dict
    over_48h_rate_dict = {}

    over_48h_rate_list = []
    if quarter >= 1 and quarter <= 4:
        if not StatisticsOver48Rate.objects.filter(yearNum=year, quarterNum=quarter):
            begin_datetime = datetime.date(year, quarter, 1)
            end_datetime = datetime.date(year, quarter * 3, calendar.mdays[quarter * 3])
            over_48h_qureyset = MalfunctionData.objects.filter(distributeTime__gte=begin_datetime, distributeTime__lte=end_datetime).values(
                'city').annotate(over_48h_amount=Count('*')).filter(processTime__gt='2880')
            order_amount_qureyset = MalfunctionData.objects.filter(distributeTime__gte=begin_datetime, distributeTime__lte=end_datetime).values(
                'city').annotate(order_amount=Count('*'))
            rate_item_list = []
            if over_48h_qureyset:
                for i in over_48h_qureyset:
                    city = i.get('city')
                    if city:
                        rate_item = StatisticsOver48Rate()
                        rate_item.yearNum = year
                        rate_item.quarterNum = quarter
                        rate_item.statisticsType = 2
                        rate_item.city = city
                        order_amount = order_amount_qureyset.get(city=city).get('order_amount')
                        order_amount = order_amount if order_amount else 1
                        over_48h_amount = i.get('over_48h_amount')
                        over_48h_amount = over_48h_amount if over_48h_amount else 0
                        rate_item.result = round(over_48h_amount / order_amount * 100, 2)
                        rate_item_list.append(rate_item)
                StatisticsOver48Rate.objects.bulk_create(rate_item_list)
            else:
                over_48h_rate_dict['msg'] = '数据库中无相关数据'
                over_48h_rate_dict['status'] = 'fail'
                return over_48h_rate_dict

        prd_1_rate = get_district_over_48h_rate(1, year, quarter)
        over_48h_rate_list += prd_1_rate
        prd_2_rate = get_district_over_48h_rate(2, year, quarter)
        over_48h_rate_list += prd_2_rate
        gd_e_rate = get_district_over_48h_rate(3, year, quarter)
        over_48h_rate_list += gd_e_rate
        gd_w_rate = get_district_over_48h_rate(4, year, quarter)
        over_48h_rate_list += gd_w_rate
        gd_n_rate = get_district_over_48h_rate(5, year, quarter)
        over_48h_rate_list += gd_n_rate
        over_48h_rate_dict['over_rate'] = over_48h_rate_list
        over_48h_rate_dict['status'] = 'success'
    else:
        over_48h_rate_dict['status'] = 'fail'
        over_48h_rate_dict['msg'] = '请求参数有误'
    return over_48h_rate_dict


# 珠1:1,珠2:2,粤东:3,粤西:4,粤北:5
def get_district_over_48h_rate(district_id, year, quarter):
    area = District.objects.get(id=district_id).district
    cities = get_cities_by_district_id(district_id)
    over_48h_rate_list = []

    for i in cities:
        over_48h_rate_item = dict()
        over_48h_rate_item['area'] = area
        over_48h_rate_item['city'] = i
        qs = StatisticsOver48Rate.objects.filter(city=i, yearNum=year, quarterNum=quarter)
        if qs:
            over_48h_rate_item['Over48Rate'] = qs[0].result
            over_48h_rate_item['area'] = area
            over_48h_rate_list.append(over_48h_rate_item)
    district_over_48h_rate = sorted(over_48h_rate_list, key=operator.itemgetter('Over48Rate'), reverse=True)
    for i in district_over_48h_rate:
        i['Over48Rate'] = str(i.get('Over48Rate'))
    return district_over_48h_rate
