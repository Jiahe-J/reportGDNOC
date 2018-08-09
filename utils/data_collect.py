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

from django.db.models import Count, Avg, Sum

from report.models import MalfunctionData, City, DistrictCity, StatisticsAmount, StatisticsInTimeRate, StatisticsDealTime, StatisticsOver48Rate, \
    District, StatisticsReason, StatisticsSpecificDealTime


def collect_order_amount(statistics_type, year, quarter, month, day):
    order_amount_queryset = []
    try:
        if statistics_type == 2:
            if 1 <= quarter <= 4:
                begin_datetime = datetime.date(year, (quarter - 1) * 3 + 1, 1)
                end_datetime = datetime.datetime(year, quarter * 3, calendar.mdays[quarter * 3], 23, 59, 59)
                if not StatisticsAmount.objects.filter(yearNum=year, quarterNum=quarter, statisticsType=2).exists():
                    order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                        'city', 'profession').annotate(order_amount=Count('profession'))
        elif statistics_type == 3:
            if 1 <= month <= 12:
                begin_datetime = datetime.date(year, month, 1)
                end_datetime = datetime.datetime(year, month, calendar.mdays[month] + (month == 2 and calendar.isleap(year)), 23, 59, 59)
                if not StatisticsAmount.objects.filter(yearNum=year, monthNum=month, statisticsType=3).exists():
                    order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                        'city', 'profession').annotate(order_amount=Count('profession'))
        elif statistics_type == 4:
            begin_datetime = datetime.date(year, month, day)
            end_datetime = begin_datetime + datetime.timedelta(days=7)
            # 如统计表中无数据则根据工单数据表进行统计:
            if not StatisticsAmount.objects.filter(yearNum=year, monthNum=month, dayNum=day, statisticsType=4).exists():
                order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                    'city', 'profession').annotate(order_amount=Count('profession'))
        elif statistics_type == 1:
            begin_datetime = datetime.date(year, 1, 1)
            end_datetime = datetime.datetime(year, 12, 31, 23, 59, 59)
            # 如统计表中无数据则根据工单数据表进行统计:
            if not StatisticsAmount.objects.filter(yearNum=year, statisticsType=1).exists():
                order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                    'city', 'profession').annotate(order_amount=Count('profession'))

        statistics_amount_list = []
        if order_amount_queryset:
            for q in order_amount_queryset:
                if q.get("city"):
                    statistics_amount = StatisticsAmount()
                    statistics_amount.yearNum = year
                    statistics_amount.quarterNum = quarter
                    statistics_amount.monthNum = month
                    statistics_amount.dayNum = day
                    statistics_amount.statisticsType = statistics_type
                    statistics_amount.city = q.get("city")
                    statistics_amount.profession = q.get('profession')
                    statistics_amount.result = q.get("order_amount")
                    statistics_amount_list.append(statistics_amount)
            StatisticsAmount.objects.bulk_create(statistics_amount_list)
            return None
    except Exception as e:
        return str(e)


def collect_order_amount_table(statistics_type, year, quarter=1, month=1, day=1, begin_datetime="", end_datetime=""):
    # 构建dict
    order_amount_dict = {}
    # 构建list
    order_amount_list = []
    try:
        if statistics_type != 5:
            msg = collect_order_amount(statistics_type, year, quarter=quarter, month=month, day=day)
            if msg:
                return {'msg': msg, 'status': 'fail'}
        # 珠1地区 Pearl River Delta 1
        prd_1_amount = get_district_order_amount(1, statistics_type=statistics_type, year=year, quarter=quarter, month=month, day=day,
                                                 begin_datetime=begin_datetime, end_datetime=end_datetime)
        order_amount_list += prd_1_amount
        prd_2_amount = get_district_order_amount(2, statistics_type=statistics_type, year=year, quarter=quarter, month=month, day=day,
                                                 begin_datetime=begin_datetime, end_datetime=end_datetime)
        order_amount_list += prd_2_amount
        gd_e_amount = get_district_order_amount(3, statistics_type=statistics_type, year=year, quarter=quarter, month=month, day=day,
                                                begin_datetime=begin_datetime, end_datetime=end_datetime)
        order_amount_list += gd_e_amount
        gd_w_amount = get_district_order_amount(4, statistics_type=statistics_type, year=year, quarter=quarter, month=month, day=day,
                                                begin_datetime=begin_datetime, end_datetime=end_datetime)
        order_amount_list += gd_w_amount
        gd_n_amount = get_district_order_amount(5, statistics_type=statistics_type, year=year, quarter=quarter, month=month, day=day,
                                                begin_datetime=begin_datetime, end_datetime=end_datetime)
        order_amount_list += gd_n_amount
        order_amount_dict['result'] = order_amount_list
        order_amount_dict['status'] = 'success'
        return order_amount_dict
    except Exception as e:
        order_amount_dict['status'] = 'fail'
        order_amount_dict['msg'] = str(e)
        return order_amount_dict


def collect_order_amount_chart(statistics_type, year, quarter=1, month=1, day=1, begin_datetime=None, end_datetime=None):
    year = int(year)
    quarter = int(quarter)
    month = int(month)
    day = int(day)
    statistics_type = int(statistics_type)
    # 构建dict
    order_amount_dict = {}
    try:
        tb_data = collect_order_amount_table(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
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


# 根据区域ID,order_admout_queryset返回排序好的区域字典列表
# 珠1:1,珠2:2,粤东:3,粤西:4,粤北:5
def get_district_order_amount(district_id, statistics_type, year, quarter, month, day, begin_datetime, end_datetime):
    area = District.objects.get(id=district_id).district
    cities = get_cities_by_district_id(district_id)
    order_amount = []
    for i in cities:
        amount_item = dict()
        amount_item['area'] = area
        amount_item['city'] = i
        if statistics_type == 2:
            result_list = StatisticsAmount.objects.filter(city=i, yearNum=year, quarterNum=quarter, statisticsType=2)
        elif statistics_type == 3:
            result_list = StatisticsAmount.objects.filter(city=i, yearNum=year, monthNum=month, statisticsType=3)
        elif statistics_type == 4:
            result_list = StatisticsAmount.objects.filter(city=i, yearNum=year, monthNum=month, dayNum=day, statisticsType=4)
        elif statistics_type == 5:
            result_list = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime), city=i).values('city',
                                                                                                                              'profession').annotate(
                result=Count('profession'))
        else:
            result_list = StatisticsAmount.objects.filter(city=i, yearNum=year, statisticsType=1)
        if result_list and statistics_type != 5:
            transmission = result_list.filter(profession="传输")[0].result if result_list.filter(profession="传输") else 0
            dynamics = result_list.filter(profession="动力")[0].result if result_list.filter(profession="动力") else 0
            exchange = result_list.filter(profession="交换")[0].result if result_list.filter(profession="交换") else 0
            AN = result_list.filter(profession="接入网")[0].result if result_list.filter(profession="接入网") else 0
            wireless = result_list.filter(profession="无线")[0].result if result_list.filter(profession="无线") else 0
            sum_amount = transmission + dynamics + exchange + AN + wireless
            amount_item['transmission'] = transmission
            amount_item['dynamics'] = dynamics
            amount_item['exchange'] = exchange
            amount_item['AN'] = AN
            amount_item['wireless'] = wireless
            amount_item['sum'] = sum_amount
            order_amount.append(amount_item)
        elif result_list and statistics_type == 5:
            transmission = result_list.filter(profession="传输")[0].get('result', 0)
            dynamics = result_list.filter(profession="动力")[0].get('result', 0)
            exchange = result_list.filter(profession="交换")[0].get('result', 0)
            AN = result_list.filter(profession="接入网")[0].get('result', 0)
            wireless = result_list.filter(profession="无线")[0].get('result', 0)
            sum_amount = transmission + dynamics + exchange + AN + wireless
            amount_item['transmission'] = transmission
            amount_item['dynamics'] = dynamics
            amount_item['exchange'] = exchange
            amount_item['AN'] = AN
            amount_item['wireless'] = wireless
            amount_item['sum'] = sum_amount
            order_amount.append(amount_item)
        else:
            raise Exception("数据库中无相关数据，时间区间：%s-%s ;类型：%s，;"
                            "%s-%s-%s 季度：%s" % (begin_datetime, end_datetime, statistics_type, year, month, day, quarter))
    district_order_amount = sorted(order_amount, key=operator.itemgetter('sum'), reverse=True)
    ls = ['transmission', 'dynamics', 'exchange', 'AN', 'wireless', 'sum']
    for i in district_order_amount:
        for p in ls:
            i[p] = str(i.get(p))
    return district_order_amount


# 根据地区id获取城市列表
def get_cities_by_district_id(district_id):
    district_city = DistrictCity.objects.filter(district=district_id)
    city_ids = []
    for i in district_city:
        city_ids.append(i.city_id)
    cities = []
    for i in City.objects.filter(id__in=city_ids):
        cities.append(i.city)
    return cities

    #  按年度,季度进行工单处理及时率汇总,返回已排序的{区域:[{城市:工单处理及时率}]}字典


def collect_deal_in_time_rate(statistics_type, year, quarter=1, month=1, day=1, begin_datetime="", end_datetime=""):
    # 构建dict
    deal_in_time_rate_dict = {}
    deal_in_time_rate_list = []
    deal_in_time_queryset = []
    order_amount_queryset = []

    if statistics_type == 2:
        if not StatisticsInTimeRate.objects.filter(yearNum=year, quarterNum=quarter, statisticsType=2).exists():
            begin_datetime = datetime.date(year, (quarter - 1) * 3 + 1, 1)
            end_datetime = datetime.datetime(year, quarter * 3, calendar.mdays[quarter * 3], 23, 59, 59)
            deal_in_time_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                'city', 'isTimeOut').annotate(deal_in_time_amount=Count('isTimeOut')).filter(isTimeOut='否')
            order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                'city').annotate(order_amount=Count('isTimeOut'))
    elif statistics_type == 3:
        if not StatisticsInTimeRate.objects.filter(yearNum=year, monthNum=month, statisticsType=3).exists():
            begin_datetime = datetime.date(year, month, 1)
            end_datetime = datetime.datetime(year, month, calendar.mdays[month], 23, 59, 59)
            deal_in_time_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                'city', 'isTimeOut').annotate(deal_in_time_amount=Count('isTimeOut')).filter(isTimeOut='否')
            order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                'city').annotate(order_amount=Count('isTimeOut'))
    elif statistics_type == 4:
        if not StatisticsInTimeRate.objects.filter(yearNum=year, monthNum=month, dayNum=day, statisticsType=4).exists():
            begin_datetime = datetime.date(year, month, day)
            end_datetime = begin_datetime + datetime.timedelta(days=7)
            deal_in_time_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                'city', 'isTimeOut').annotate(deal_in_time_amount=Count('isTimeOut')).filter(isTimeOut='否')
            order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                'city').annotate(order_amount=Count('isTimeOut'))
    elif statistics_type == 1:
        if not StatisticsInTimeRate.objects.filter(yearNum=year, statisticsType=1).exists():
            begin_datetime = datetime.date(year, 1, 1)
            end_datetime = datetime.datetime(year, 12, 31, 23, 59, 59)
            deal_in_time_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                'city', 'isTimeOut').annotate(deal_in_time_amount=Count('isTimeOut')).filter(isTimeOut='否')
            order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                'city').annotate(order_amount=Count('isTimeOut'))
    if deal_in_time_queryset and order_amount_queryset:
        rate_item_list = []
        for i in deal_in_time_queryset:
            city = i.get('city')
            if city:
                rate_item = StatisticsInTimeRate()
                rate_item.yearNum = year
                rate_item.quarterNum = quarter
                rate_item.monthNum = month
                rate_item.dayNum = day
                rate_item.statisticsType = statistics_type
                rate_item.city = city
                order_amount = order_amount_queryset.get(city=city).get('order_amount')
                order_amount = order_amount if order_amount else 1
                in_time_rate_amount = i.get('deal_in_time_amount')
                in_time_rate_amount = in_time_rate_amount if in_time_rate_amount else 0
                rate_item.result = round(in_time_rate_amount / order_amount * 100, 2) if order_amount != 0 else 0
                rate_item_list.append(rate_item)
        StatisticsInTimeRate.objects.bulk_create(rate_item_list)

    # 根据区域ID,order_deal_in_time_queryset返回排序好的区域字典列表
    # 珠1:1,珠2:2,粤东:3,粤西:4,粤北:5
    try:
        prd_1_rate = get_district_deal_in_time_rate(1, statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        deal_in_time_rate_list += prd_1_rate
        prd_2_rate = get_district_deal_in_time_rate(2, statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        deal_in_time_rate_list += prd_2_rate
        gd_e_rate = get_district_deal_in_time_rate(3, statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        deal_in_time_rate_list += gd_e_rate
        gd_w_rate = get_district_deal_in_time_rate(4, statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        deal_in_time_rate_list += gd_w_rate
        gd_n_rate = get_district_deal_in_time_rate(5, statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        deal_in_time_rate_list += gd_n_rate
        deal_in_time_rate_dict['result'] = deal_in_time_rate_list
        deal_in_time_rate_dict['status'] = 'success'
        return deal_in_time_rate_dict
    except Exception as e:
        deal_in_time_rate_dict['status'] = 'fail'
        deal_in_time_rate_dict['msg'] = str(e)
        return deal_in_time_rate_dict


def get_district_deal_in_time_rate(district_id, statistics_type, year, quarter, month, day, begin_datetime, end_datetime):
    area = District.objects.get(id=district_id).district
    cities = get_cities_by_district_id(district_id)
    deal_in_time_rate_list = []
    deal_in_time_queryset = []
    order_amount_queryset = []
    for i in cities:
        deal_in_time_rate_item = dict()
        deal_in_time_rate_item['area'] = area
        deal_in_time_rate_item['city'] = i
        if statistics_type == 2:
            qs = StatisticsInTimeRate.objects.filter(city=i, yearNum=year, quarterNum=quarter, statisticsType=2)
        elif statistics_type == 3:
            qs = StatisticsInTimeRate.objects.filter(city=i, yearNum=year, monthNum=month, statisticsType=3)
        elif statistics_type == 4:
            qs = StatisticsInTimeRate.objects.filter(city=i, yearNum=year, monthNum=month, dayNum=day, statisticsType=4)
        elif statistics_type == 1:
            qs = StatisticsInTimeRate.objects.filter(city=i, yearNum=year, statisticsType=1)
        else:
            qs = None
            deal_in_time_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime),
                                                                   city=i).values(
                'city', 'isTimeOut').annotate(deal_in_time_amount=Count('isTimeOut')).filter(isTimeOut='否')
            order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime),
                                                                   city=i).values(
                'city').annotate(order_amount=Count('isTimeOut'))
        if qs and statistics_type != 5:
            deal_in_time_rate_item['IntimeRate'] = qs[0].result
            deal_in_time_rate_list.append(deal_in_time_rate_item)
        elif deal_in_time_queryset and order_amount_queryset and statistics_type == 5:
            order_amount = order_amount_queryset[0].get('order_amount')
            in_time_rate_amount = deal_in_time_queryset[0].get('deal_in_time_amount')
            deal_in_time_rate_item['IntimeRate'] = round(in_time_rate_amount / order_amount * 100, 2) if order_amount != 0 else 0
            deal_in_time_rate_list.append(deal_in_time_rate_item)
        else:
            raise Exception("数据库中无相关数据，时间区间：%s-%s ;类型：%s，;"
                            "%s-%s-%s 季度：%s" % (begin_datetime, end_datetime, statistics_type, year, month, day, quarter))
    district_deal_in_time_rate = sorted(deal_in_time_rate_list, key=operator.itemgetter('IntimeRate'), reverse=True)
    for i in district_deal_in_time_rate:
        i['IntimeRate'] = str(i.get('IntimeRate'))
    return district_deal_in_time_rate


# 故障平均处理时长统计,按年度,季度进行工单处理及时率汇总
def collect_deal_time(statistics_type, year, quarter=1, month=1, day=1, begin_datetime="", end_datetime=""):
    deal_time_dict = {}
    deal_time_list = []
    deal_time_queryset = []
    if statistics_type == 2:
        if not StatisticsDealTime.objects.filter(statisticsType=2, yearNum=year, quarterNum=quarter).exists():
            begin_datetime = datetime.date(year, (quarter - 1) * 3 + 1, 1)
            end_datetime = datetime.datetime(year, quarter * 3, calendar.mdays[quarter * 3], 23, 59, 59)
            deal_time_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                'city').annotate(average_time=Avg('processTime'))
    elif statistics_type == 3:
        if not StatisticsDealTime.objects.filter(statisticsType=3, yearNum=year, monthNum=month).exists():
            begin_datetime = datetime.date(year, (quarter - 1) * 3 + 1, 1)
            end_datetime = datetime.datetime(year, month, calendar.mdays[month], 23, 59, 59)
            deal_time_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                'city').annotate(average_time=Avg('processTime'))
    elif statistics_type == 4:
        if not StatisticsDealTime.objects.filter(statisticsType=4, yearNum=year, monthNum=month, dayNum=day).exists():
            begin_datetime = datetime.date(year, (quarter - 1) * 3 + 1, 1)
            end_datetime = begin_datetime + datetime.timedelta(days=7)
            deal_time_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                'city').annotate(average_time=Avg('processTime'))

    elif statistics_type == 1:
        if not StatisticsDealTime.objects.filter(statisticsType=1, yearNum=year).exists():
            begin_datetime = datetime.date(year, 1, 1)
            end_datetime = datetime.datetime(year, 12, 31, 23, 59, 59)
            deal_time_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                'city').annotate(average_time=Avg('processTime'))
    if deal_time_queryset:
        process_time_list = []
        for i in deal_time_queryset:
            city = i.get('city')
            if city:
                process_item = StatisticsDealTime()
                process_item.yearNum = year
                process_item.quarterNum = quarter
                process_item.monthNum = month
                process_item.dayNum = day
                process_item.city = city
                process_item.statisticsType = statistics_type
                process_item.result = round(i.get('average_time') / 60, 2)
                process_time_list.append(process_item)
        StatisticsDealTime.objects.bulk_create(process_time_list)

    try:
        prd_1_rate = get_district_deal_time(1, statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        deal_time_list += prd_1_rate
        prd_2_rate = get_district_deal_time(2, statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        deal_time_list += prd_2_rate
        gd_e_rate = get_district_deal_time(3, statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        deal_time_list += gd_e_rate
        gd_w_rate = get_district_deal_time(4, statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        deal_time_list += gd_w_rate
        gd_n_rate = get_district_deal_time(5, statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        deal_time_list += gd_n_rate
        deal_time_dict['result'] = deal_time_list
        deal_time_dict['status'] = 'success'
        return deal_time_dict
    except Exception as e:
        deal_time_dict['status'] = 'fail'
        deal_time_dict['msg'] = str(e)
        return deal_time_dict


def get_district_deal_time(district_id, statistics_type, year, quarter, month, day, begin_datetime, end_datetime):
    area = District.objects.get(id=district_id).district
    cities = get_cities_by_district_id(district_id)
    deal_time_list = []
    for i in cities:
        deal_time_item = dict()
        deal_time_item['area'] = area
        deal_time_item['city'] = i
        if statistics_type == 2:
            qs = StatisticsDealTime.objects.filter(statisticsType=2, city=i, yearNum=year, quarterNum=quarter)
        elif statistics_type == 3:
            qs = StatisticsDealTime.objects.filter(statisticsType=3, city=i, yearNum=year, monthNum=month)
        elif statistics_type == 4:
            qs = StatisticsDealTime.objects.filter(statisticsType=4, city=i, yearNum=year, monthNum=month, dayNum=day)
        elif statistics_type == 1:
            qs = StatisticsDealTime.objects.filter(statisticsType=1, city=i, yearNum=year)
        else:
            qs = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime), city=i).values(
                'city').annotate(processTime=Avg('processTime'))

        if qs and statistics_type != 5:
            deal_time_item['AverageTime'] = qs[0].result
            deal_time_list.append(deal_time_item)
        elif qs and statistics_type == 5:
            deal_time_item['AverageTime'] = round(qs[0].get('processTime') / 60, 2)
            deal_time_list.append(deal_time_item)
        else:
            raise Exception("数据库中无相关数据，时间区间：%s-%s ;类型：%s，;"
                            "%s-%s-%s 季度：%s" % (begin_datetime, end_datetime, statistics_type, year, month, day, quarter))
    district_deal_time = sorted(deal_time_list, key=operator.itemgetter('AverageTime'), reverse=True)
    for i in district_deal_time:
        i['AverageTime'] = str(i.get('AverageTime'))
    return district_deal_time


#  按年度,季度进行超48小时工单占比统计
def collect_over_48h_rate(statistics_type, year, quarter=1, month=1, day=1, begin_datetime='', end_datetime=''):
    # 构建dict
    over_48h_rate_dict = {}
    over_48h_rate_list = []
    over_48h_queryset = []
    order_amount_queryset = []
    if statistics_type == 2:
        if not StatisticsOver48Rate.objects.filter(statisticsType=2, yearNum=year, quarterNum=quarter).exists():
            begin_datetime = datetime.date(year, (quarter - 1) * 3 + 1, 1)
            end_datetime = datetime.datetime(year, quarter * 3, calendar.mdays[quarter * 3], 23, 59, 59)
            over_48h_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime),
                                                               processTime__gt='2880').values(
                'city').annotate(over_48h_amount=Count('city'))
            order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                'city').annotate(order_amount=Count('city'))
    elif statistics_type == 3:
        if not StatisticsOver48Rate.objects.filter(statisticsType=3, yearNum=year, monthNum=month).exists():
            begin_datetime = datetime.date(year, month, 1)
            end_datetime = datetime.datetime(year, month, calendar.mdays[month], 23, 59, 59)
            over_48h_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime),
                                                               processTime__gt='2880').values(
                'city').annotate(over_48h_amount=Count('city'))
            order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                'city').annotate(order_amount=Count('city'))
    elif statistics_type == 4:
        if not StatisticsOver48Rate.objects.filter(statisticsType=4, yearNum=year, monthNum=month, dayNum=day).exists():
            begin_datetime = datetime.date(year, month, 1)
            end_datetime = begin_datetime + datetime.timedelta(days=7)
            over_48h_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime),
                                                               processTime__gt='2880').values(
                'city').annotate(over_48h_amount=Count('city'))
            order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                'city').annotate(order_amount=Count('city'))
    elif statistics_type == 1:
        if not StatisticsOver48Rate.objects.filter(statisticsType=1, yearNum=year).exists():
            begin_datetime = datetime.date(year, 1, 1)
            end_datetime = datetime.datetime(year, 12, 31, 23, 59, 59)
            over_48h_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime),
                                                               processTime__gt='2880').values(
                'city').annotate(over_48h_amount=Count('city'))
            order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                'city').annotate(order_amount=Count('city'))
    if over_48h_queryset:
        rate_item_list = []
        for i in over_48h_queryset:
            city = i.get('city')
            if city:
                rate_item = StatisticsOver48Rate()
                rate_item.yearNum = year
                rate_item.quarterNum = quarter
                rate_item.monthNum = month
                rate_item.dayNum = day
                rate_item.statisticsType = statistics_type
                rate_item.city = city
                order_amount = order_amount_queryset.get(city=city).get('order_amount')
                order_amount = order_amount if order_amount else 1
                over_48h_amount = i.get('over_48h_amount')
                over_48h_amount = over_48h_amount if over_48h_amount else 0
                rate_item.result = round(over_48h_amount / order_amount * 100, 2) if order_amount != 0 else 0
                rate_item_list.append(rate_item)
        StatisticsOver48Rate.objects.bulk_create(rate_item_list)
    try:
        prd_1_rate = get_district_over_48h_rate(1, statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        over_48h_rate_list += prd_1_rate
        prd_2_rate = get_district_over_48h_rate(2, statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        over_48h_rate_list += prd_2_rate
        gd_e_rate = get_district_over_48h_rate(3, statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        over_48h_rate_list += gd_e_rate
        gd_w_rate = get_district_over_48h_rate(4, statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        over_48h_rate_list += gd_w_rate
        gd_n_rate = get_district_over_48h_rate(5, statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        over_48h_rate_list += gd_n_rate
        over_48h_rate_dict['result'] = over_48h_rate_list
        over_48h_rate_dict['status'] = 'success'
        return over_48h_rate_dict
    except Exception as e:
        over_48h_rate_dict['msg'] = str(e)
        over_48h_rate_dict['status'] = 'fail'
        return over_48h_rate_dict


# 珠1:1,珠2:2,粤东:3,粤西:4,粤北:5
def get_district_over_48h_rate(district_id, statistics_type, year, quarter, month, day, begin_datetime, end_datetime):
    area = District.objects.get(id=district_id).district
    cities = get_cities_by_district_id(district_id)
    over_48h_rate_list = []
    over_48h_queryset = []
    order_amount_queryset = []
    for i in cities:
        over_48h_rate_item = dict()
        over_48h_rate_item['area'] = area
        over_48h_rate_item['city'] = i
        if statistics_type == 2:
            qs = StatisticsOver48Rate.objects.filter(statisticsType=2, city=i, yearNum=year, quarterNum=quarter)
        elif statistics_type == 3:
            qs = StatisticsOver48Rate.objects.filter(statisticsType=3, city=i, yearNum=year, monthNum=month)
        elif statistics_type == 4:
            qs = StatisticsOver48Rate.objects.filter(statisticsType=4, city=i, yearNum=year, monthNum=month, dayNum=day)
        elif statistics_type == 1:
            qs = StatisticsOver48Rate.objects.filter(statisticsType=1, city=i, yearNum=year)
        else:
            qs = []
            over_48h_queryset = MalfunctionData.objects.filter(ddistributeTime__range=(begin_datetime, end_datetime), city=i,
                                                               processTime__gt='2880').values(
                'city').annotate(over_48h_amount=Count('*'))
            order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime),
                                                                   city=i).values(
                'city').annotate(order_amount=Count('*'))
        if qs and statistics_type != 5:
            over_48h_rate_item['Over48Rate'] = qs[0].result
            over_48h_rate_list.append(over_48h_rate_item)
        elif over_48h_queryset and order_amount_queryset and statistics_type == 5:
            over_48_amount = over_48h_queryset[0].get('over_48h_amount')
            order_amount = order_amount_queryset[0].get('order_amount')
            over_48h_rate_item['Over48Rate'] = round(over_48_amount / order_amount * 100, 2) if order_amount != 0 else 0
            over_48h_rate_list.append(over_48h_rate_item)

        else:
            raise Exception("数据库中无相关数据，时间区间：%s-%s ;类型：%s，;"
                            "%s-%s-%s 季度：%s" % (begin_datetime, end_datetime, statistics_type, year, month, day, quarter))
    district_over_48h_rate = sorted(over_48h_rate_list, key=operator.itemgetter('Over48Rate'), reverse=True)
    for i in district_over_48h_rate:
        i['Over48Rate'] = str(i.get('Over48Rate'))
    return district_over_48h_rate


def collect_deal_quality(statistics_type, year, quarter, month, day, begin_datetime, end_datetime):
    result_list = []
    result = dict()
    try:
        intime_rate_result = collect_deal_in_time_rate(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        deal_time_result = collect_deal_time(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        ovre48_rate_result = collect_over_48h_rate(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        for i in range(1, 6):
            cities = get_cities_by_district_id(i)
            district = District.objects.get(id=i).district
            for city in cities:
                result_item = dict()
                result_item['area'] = district
                result_item['city'] = city
                for intime_rate_item in intime_rate_result.get('result'):
                    if intime_rate_item.get("city") == city:
                        result_item['IntimeRate'] = intime_rate_item.get('IntimeRate')
                for deal_time_item in deal_time_result.get('result'):
                    if deal_time_item.get('city') == city:
                        result_item['AverageTime'] = deal_time_item.get('AverageTime')
                for ovre48_rate_item in ovre48_rate_result.get('result'):
                    if ovre48_rate_item.get('city') == city:
                        result_item['Over48Rate'] = ovre48_rate_item.get("Over48Rate")
                result_list.append(result_item)

        result['status'] = "success"
        result['result'] = result_list
        return result
    except Exception as e:
        result['status'] = "fail"
        result['msg'] = str(e)
        return result


def collect_specific_dealtime_amount(statistics_type, year=1, quarter=1, month=1, day=1, begin_datetime="", end_datetime=""):
    result_dict = {}
    if statistics_type != 5:
        begin_datetime = ""
        end_datetime = ""
    if statistics_type == 1:
        if not StatisticsSpecificDealTime.objects.filter(statisticsType=1, yearNum=year).exists():
            begin_datetime = datetime.date(year, 1, 1)
            end_datetime = datetime.datetime(year, 12, 31, 23, 59, 59)
    elif statistics_type == 2:
        if not StatisticsSpecificDealTime.objects.filter(statisticsType=2, yearNum=year, quarterNum=quarter).exists():
            begin_datetime = datetime.date(year, (quarter - 1) * 3 + 1, 1)
            end_datetime = datetime.datetime(year, quarter * 3, calendar.mdays[quarter * 3], 23, 59, 59)
    elif statistics_type == 3:
        if not StatisticsSpecificDealTime.objects.filter(statisticsType=3, yearNum=year, monthNum=month).exists():
            begin_datetime = datetime.date(year, month, 1)
            end_datetime = datetime.datetime(year, month, calendar.mdays[month], 23, 59, 59)
    elif statistics_type == 4:
        if not StatisticsSpecificDealTime.objects.filter(statisticsType=4, yearNum=year, monthNum=month, dayNum=day).exists():
            begin_datetime = datetime.date(year, month, 1)
            end_datetime = begin_datetime + datetime.timedelta(days=7)
    if begin_datetime and statistics_type != 5:
        item_list = []
        reason_itme_list = []
        reason_qs = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values('city',
                                                                                                                'malfunctionJudgment').annotate(
            sum_dealtime=Sum('processTime'), sum_amount=Count('*'))
        for city_obj in City.objects.all():
            print(city_obj.city)
            for reason in ['线路故障', '设备故障']:
                item = StatisticsSpecificDealTime(city=city_obj.city, reason=reason, statisticsType=statistics_type, yearNum=year, monthNum=month,
                                                  dayNum=day)
                reason_item = StatisticsReason(city=city_obj.city, reason=reason, statisticsType=statistics_type, yearNum=year, monthNum=month,
                                               dayNum=day)
                line_qs = reason_qs.filter(malfunctionJudgment__contains=reason, city=city_obj.city).values('sum_dealtime', 'sum_amount')
                sum_dealtime = 0
                sum_amount = 0
                for i in line_qs:
                    sum_dealtime += i.get('sum_dealtime')
                    sum_amount += i.get('sum_amount')
                item.result = round(sum_dealtime / sum_amount / 60, 2) if sum_amount != 0 else 0
                reason_item.result = sum_amount
                item_list.append(item)
                reason_itme_list.append(reason_item)
            poweroff_item = StatisticsSpecificDealTime(city=city_obj.city, reason='停电', statisticsType=statistics_type, yearNum=year, monthNum=month,
                                                       dayNum=day)
            reason_poweroff_item = StatisticsSpecificDealTime(city=city_obj.city, reason='停电', statisticsType=statistics_type, yearNum=year,
                                                              monthNum=month,
                                                              dayNum=day)
            environment_item = StatisticsSpecificDealTime(city=city_obj.city, reason='动环故障', statisticsType=statistics_type, yearNum=year,
                                                          monthNum=month,
                                                          dayNum=day)
            reason_environment_item = StatisticsSpecificDealTime(city=city_obj.city, reason='动环故障', statisticsType=statistics_type, yearNum=year,
                                                                 monthNum=month,
                                                                 dayNum=day)
            all_env_qs = reason_qs.filter(malfunctionJudgment__contains='动环故障', city=city_obj.city).values('malfunctionJudgment', 'sum_dealtime',
                                                                                                           'sum_amount')
            all_env_sum_dealtime = 0
            all_env_sum_amount = 0
            for i in all_env_qs:
                all_env_sum_dealtime += i.get('sum_dealtime')
                all_env_sum_amount += i.get('sum_amount')
            poweroff_qs = all_env_qs.filter(malfunctionJudgment__contains='停电')
            poweroff_sum_dealtime = 0
            poweroff_sum_amount = 0
            for i in poweroff_qs:
                poweroff_sum_dealtime += i.get('sum_dealtime')
                poweroff_sum_amount += i.get('sum_amount')
            poweroff_item.result = round(poweroff_sum_dealtime / poweroff_sum_amount / 60, 2) if poweroff_sum_amount != 0 else 0
            reason_poweroff_item.result = poweroff_sum_amount
            environment_item.result = round((all_env_sum_dealtime - poweroff_sum_dealtime) / (all_env_sum_amount - poweroff_sum_amount) / 60, 2) \
                if (all_env_sum_amount - poweroff_sum_amount) != 0 else 0
            reason_environment_item.result = all_env_sum_amount - poweroff_sum_amount

            item_list.append(poweroff_item)
            item_list.append(environment_item)

            reason_itme_list.append(reason_poweroff_item)
            reason_itme_list.append(reason_environment_item)

            other_item = StatisticsSpecificDealTime(city=city_obj.city, reason='其他', statisticsType=statistics_type, yearNum=year, monthNum=month,
                                                    dayNum=day)
            reason_other_item = StatisticsReason(city=city_obj.city, reason='其他', statisticsType=statistics_type, yearNum=year, monthNum=month,
                                                 dayNum=day)
            other_qs = reason_qs.filter(city=city_obj.city).exclude(malfunctionJudgment__contains='动环故障').exclude(
                malfunctionJudgment__contains='线路故障').exclude(malfunctionJudgment__contains='设备故障').values('malfunctionJudgment', 'sum_dealtime',
                                                                                                           'sum_amount')
            other_sum_dealtime = 0
            other_sum_amount = 0
            for i in other_qs:
                other_sum_dealtime += i.get('sum_dealtime', 0)
                other_sum_amount += i.get('sum_amount', 0)
            other_item.result = round(other_sum_dealtime / other_sum_amount / 60, 2) if other_sum_amount != 0 else 0
            reason_other_item.result = other_sum_amount

            item_list.append(other_item)
            reason_itme_list.append(reason_other_item)
        StatisticsSpecificDealTime.objects.bulk_create(item_list)
        StatisticsReason.objects.bulk_create(reason_itme_list)
    try:
        result_dict['result'] = get_specific_dealtime_amount(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        result_dict['status'] = 'success'
        return result_dict
    except Exception as e:
        result_dict['status'] = 'fail'
        result_dict['msg'] = str(e)


def get_specific_dealtime_amount(statistics_type, year, quarter, month, day, begin_datetime, end_datetime):
    result_list = []
    if statistics_type == 2:
        qs = StatisticsSpecificDealTime.objects.filter(statisticsType=2, yearNum=year, quarterNum=quarter)
    elif statistics_type == 3:
        qs = StatisticsSpecificDealTime.objects.filter(statisticsType=3, yearNum=year, monthNum=month)
    elif statistics_type == 4:
        qs = StatisticsSpecificDealTime.objects.filter(statisticsType=4, yearNum=year, monthNum=month, dayNum=day)
    elif statistics_type == 1:
        qs = StatisticsSpecificDealTime.objects.filter(statisticsType=1, yearNum=year)
    else:
        qs = []
    if qs and statistics_type != 5:
        # 按地区获取结果
        for district_id in range(1, 6):
            cities = get_cities_by_district_id(district_id)
            for city in cities:
                result_item = dict()
                city_qs = qs.filter(city=city)
                result_item['area'] = DistrictCity.objects.get(city=City.objects.get(city=city).id).district.district
                result_item['city'] = city
                result_item['line_time'] = str(city_qs.filter(reason='线路故障')[0].result)
                result_item['power_time'] = str(city_qs.filter(reason='停电')[0].result)
                result_item['environment_time'] = str(city_qs.filter(reason='动环故障')[0].result)
                result_item['equipment_time'] = str(city_qs.filter(reason='设备故障')[0].result)
                result_item['other_time'] = str(city_qs.filter(reason='其他')[0].result)
                result_list.append(result_item)
        return result_list
    elif statistics_type == 5:
        qs = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values('city',
                                                                                                         'malfunctionJudgment').annotate(
            sum_dealtime=Sum('processTime'), sum_amount=Count('*'))
        for district_id in range(1, 6):
            cities = get_cities_by_district_id(district_id)
            for city in cities:
                print(city)
                result_item = dict()
                city_qs = qs.filter(city=city)
                result_item['area'] = District.objects.get(id=district_id).district
                result_item['city'] = city
                line_qs = city_qs.filter(malfunctionJudgment__contains='线路故障')
                line_dealtime = 0
                line_amount = 0
                for i in line_qs:
                    line_dealtime += i.get('sum_dealtime', 0)
                    line_amount += i.get('sum_amount', 0)
                result_item['line_time'] = str(round(line_dealtime / line_amount / 60, 2) if line_amount != 0 else 0)
                result_item['line_amount'] = str(line_amount)

                equipment_qs = city_qs.filter(malfunctionJudgment__contains='设备故障')
                equipment_dealtime = 0
                equipment_amount = 0
                for i in equipment_qs:
                    equipment_dealtime += i.get('sum_dealtime', 0)
                    equipment_amount += i.get('sum_amount', 0)
                result_item['equipment_time'] = str(round(equipment_dealtime / equipment_amount / 60, 2) if equipment_amount != 0 else 0)
                result_item['equipment_amount'] = str(equipment_amount)

                environment_qs = city_qs.filter(malfunctionJudgment__contains='动环故障').exclude(malfunctionJudgment__contains='停电')
                environment_dealtime = 0
                environment_amount = 0
                for i in environment_qs:
                    environment_dealtime += i.get('sum_dealtime', 0)
                    environment_amount += i.get('sum_amount', 0)
                result_item['environment_time'] = str(round(environment_dealtime / environment_amount / 60, 2) if environment_amount != 0 else 0)
                result_item['environment_amount'] = str(environment_amount)

                power_qs = city_qs.filter(malfunctionJudgment__contains='停电')
                power_dealtime = 0
                power_amount = 0
                for i in power_qs:
                    power_dealtime += i.get('sum_dealtime', 0)
                    power_amount += i.get('sum_amount', 0)
                result_item['power_time'] = str(round(power_dealtime / power_amount / 60, 2) if power_amount != 0 else 0)
                result_item['power_amount'] = str(power_amount)

                other_qs = city_qs.exclude(malfunctionJudgment__contains='线路故障').exclude(malfunctionJudgment__contains='设备故障').exclude(
                    malfunctionJudgment__contains='动环故障')

                other_dealtime = 0
                other_amount = 0
                for i in other_qs:
                    other_dealtime += i.get('sum_dealtime', 0)
                    other_amount += i.get('sum_amount', 0)
                result_item['other_time'] = str(round(other_dealtime / other_amount / 60, 2) if other_amount != 0 else 0)
                result_item['other_amount'] = str(other_amount)

                result_list.append(result_item)
        return result_list
