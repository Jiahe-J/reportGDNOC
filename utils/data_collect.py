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

from report.models import MalfunctionData, City, DistrictCity, StatisticsQuarterlyAmount, District, StatisticsQuarterlyQuality


def collect_order_amount(statistics_type, year, quarter, month, day):
    order_amount_queryset = []
    try:
        if statistics_type == 2:
            if 1 <= quarter <= 4:
                begin_datetime = datetime.date(year, (quarter - 1) * 3 + 1, 1)
                end_datetime = datetime.datetime(year, quarter * 3, calendar.mdays[quarter * 3], 23, 59, 59)
                if not StatisticsQuarterlyAmount.objects.filter(yearNum=year, quarterNum=quarter, statisticsType=2).exists():
                    order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                        'city', 'profession').annotate(order_amount=Count('profession'))
        elif statistics_type == 3:
            if 1 <= month <= 12:
                begin_datetime = datetime.date(year, month, 1)
                end_datetime = datetime.datetime(year, month, calendar.mdays[month] + (month == 2 and calendar.isleap(year)), 23, 59, 59)
                if not StatisticsQuarterlyAmount.objects.filter(yearNum=year, monthNum=month, statisticsType=3).exists():
                    order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                        'city', 'profession').annotate(order_amount=Count('profession'))
        elif statistics_type == 4:
            begin_datetime = datetime.date(year, month, day)
            end_datetime = begin_datetime + datetime.timedelta(days=7)
            # 如统计表中无数据则根据工单数据表进行统计:
            if not StatisticsQuarterlyAmount.objects.filter(yearNum=year, monthNum=month, dayNum=day, statisticsType=4).exists():
                order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                    'city', 'profession').annotate(order_amount=Count('profession'))
        elif statistics_type == 1:
            begin_datetime = datetime.date(year, 1, 1)
            end_datetime = datetime.datetime(year, 12, 31, 23, 59, 59)
            # 如统计表中无数据则根据工单数据表进行统计:
            if not StatisticsQuarterlyAmount.objects.filter(yearNum=year, statisticsType=1).exists():
                order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
                    'city', 'profession').annotate(order_amount=Count('profession'))

        statistics_amount_list = []
        if order_amount_queryset:
            for q in order_amount_queryset:
                if q.get("city"):
                    statistics_amount = StatisticsQuarterlyAmount()
                    statistics_amount.yearNum = year
                    statistics_amount.quarterNum = quarter
                    statistics_amount.monthNum = month
                    statistics_amount.dayNum = day
                    statistics_amount.statisticsType = statistics_type
                    statistics_amount.city = q.get("city")
                    statistics_amount.profession = q.get('profession')
                    statistics_amount.result = q.get("order_amount")
                    statistics_amount_list.append(statistics_amount)
            StatisticsQuarterlyAmount.objects.bulk_create(statistics_amount_list)
            return None
    except Exception as e:
        return str(e)


def collect_order_amount_table(statistics_type, year, quarter=1, month=1, day=1, begin_datetime="", end_datetime=""):
    # 构建dict
    order_amount_dict = {}
    # 构建list
    order_amount_list = []
    try:
        # 珠1地区 Pearl River Delta 1
        prd_1_amount = get_district_order_amount(statistics_type=statistics_type, year=year, quarter=quarter, month=month, day=day,
                                                 begin_datetime=begin_datetime, end_datetime=end_datetime)
        order_amount_list += prd_1_amount
        order_amount_dict['result'] = order_amount_list
        order_amount_dict['status'] = 'success'
        return order_amount_dict
    except Exception as e:
        order_amount_dict['status'] = 'fail'
        order_amount_dict['msg'] = str(e)
        return order_amount_dict


# 根据区域ID,order_admout_queryset返回排序好的区域字典列表
# 珠1:1,珠2:2,粤东:3,粤西:4,粤北:5
# 1 珠三角 2 粤东  3 粤西
def get_district_order_amount(statistics_type, year, quarter, month, day, begin_datetime, end_datetime):
    order_amount_list = []
    result_list = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values('city',
                                                                                                              'profession').annotate(
        result=Count('city'))
    for district in District.objects.all():
        area = district.district
        cities = get_cities_by_district_id(district.id)
        order_amount = []

        for i in cities:
            amount_item = dict()
            amount_item['area'] = area
            amount_item['city'] = i
            if result_list:
                city_result_list = result_list.filter(city=i)
                transmission = city_result_list.get(profession="传输").get('result', 0)
                dynamics = city_result_list.get(profession="动力").get('result', 0)
                exchange = city_result_list.get(profession="交换").get('result', 0)
                AN = city_result_list.get(profession="接入网").get('result', 0)
                wireless = city_result_list.get(profession="无线").get('result', 0)
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
        # district_order_amount = sorted(order_amount, key=operator.itemgetter('sum'), reverse=True)
        ls = ['transmission', 'dynamics', 'exchange', 'AN', 'wireless', 'sum']
        for i in order_amount:
            for p in ls:
                i[p] = str(i.get(p))
        order_amount_list += order_amount
    return order_amount_list


# 根据地区id获取城市列表
def get_cities_by_district_id(district_id):
    cities = []
    for i in City.objects.filter(districtcity__district=district_id):
        cities.append(i.city)
    return cities


#  按年度,季度进行工单处理及时率汇总,返回已排序的{区域:[{城市:工单处理及时率}]}字典
def collect_deal_in_time_rate(statistics_type, year, quarter=1, month=1, day=1, begin_datetime="", end_datetime=""):
    # 构建dict
    deal_in_time_rate_dict = {}
    deal_in_time_rate_list = []

    # 根据区域ID,order_deal_in_time_queryset返回排序好的区域字典列表
    # 珠1:1,珠2:2,粤东:3,粤西:4,粤北:5
    try:
        prd_1_rate = get_district_deal_in_time_rate(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        deal_in_time_rate_list += prd_1_rate
        deal_in_time_rate_dict['result'] = deal_in_time_rate_list
        deal_in_time_rate_dict['status'] = 'success'
        return deal_in_time_rate_dict
    except Exception as e:
        deal_in_time_rate_dict['status'] = 'fail'
        deal_in_time_rate_dict['msg'] = str(e)
        return deal_in_time_rate_dict


def get_district_deal_in_time_rate(statistics_type, year, quarter, month, day, begin_datetime, end_datetime):
    intime_list = []
    if 1:
        deal_in_time_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime), isTimeOut='否'
                                                               ).values(
            'city').annotate(deal_in_time_amount=Count('city'))
        order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime),
                                                               ).values(
            'city').annotate(order_amount=Count('city'))
    for district in District.objects.all():
        area = district.district
        cities = get_cities_by_district_id(district.id)
        deal_in_time_rate_list = []
        for i in cities:
            deal_in_time_rate_item = dict()
            deal_in_time_rate_item['area'] = area
            deal_in_time_rate_item['city'] = i
            if deal_in_time_queryset and order_amount_queryset and statistics_type == 5:
                city_amount_qs = order_amount_queryset.filter(city=i)[0]
                city_deal_intime_qs = deal_in_time_queryset.filter(city=i)[0]
                order_amount = city_amount_qs.get('order_amount')
                in_time_rate_amount = city_deal_intime_qs.get('deal_in_time_amount')
                deal_in_time_rate_item['IntimeRate'] = round(in_time_rate_amount / order_amount * 100, 2) if order_amount != 0 else 0
                deal_in_time_rate_list.append(deal_in_time_rate_item)
            else:
                raise Exception("数据库中无相关数据，时间区间：%s-%s ;类型：%s，;"
                                "%s-%s-%s 季度：%s" % (begin_datetime, end_datetime, statistics_type, year, month, day, quarter))
        district_deal_in_time_rate = sorted(deal_in_time_rate_list, key=operator.itemgetter('IntimeRate'), reverse=True)
        for i in district_deal_in_time_rate:
            i['IntimeRate'] = str(i.get('IntimeRate'))
        intime_list += district_deal_in_time_rate
    return intime_list


# 故障平均处理时长统计,按年度,季度进行工单处理及时率汇总
def collect_deal_time(statistics_type, year, quarter=1, month=1, day=1, begin_datetime="", end_datetime=""):
    deal_time_dict = {}
    deal_time_list = []

    try:
        prd_1_rate = get_district_deal_time(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        deal_time_list += prd_1_rate

        deal_time_dict['result'] = deal_time_list
        deal_time_dict['status'] = 'success'
        return deal_time_dict
    except Exception as e:
        deal_time_dict['status'] = 'fail'
        deal_time_dict['msg'] = str(e)
        return deal_time_dict


def get_district_deal_time(statistics_type, year, quarter, month, day, begin_datetime, end_datetime):
    deal_time_result = []
    if 1:
        qs = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
            'city').annotate(processTime=Avg('processTime'))

    for district in District.objects.all():
        area = district.district
        cities = get_cities_by_district_id(district.id)
        deal_time_list = []
        for i in cities:
            deal_time_item = dict()
            deal_time_item['area'] = area
            deal_time_item['city'] = i
            city_qs = qs.filter(city=i)
            if qs and statistics_type != 5:
                deal_time_item['AverageTime'] = city_qs[0].result
                deal_time_list.append(deal_time_item)
            elif city_qs and statistics_type == 5:
                deal_time_item['AverageTime'] = round(city_qs[0].get('processTime') / 60, 2)
                deal_time_list.append(deal_time_item)
            else:
                raise Exception("数据库中无相关数据，时间区间：%s-%s ;类型：%s，;"
                                "%s-%s-%s 季度：%s" % (begin_datetime, end_datetime, statistics_type, year, month, day, quarter))
        district_deal_time = sorted(deal_time_list, key=operator.itemgetter('AverageTime'), reverse=True)
        for i in district_deal_time:
            i['AverageTime'] = str(i.get('AverageTime'))
        deal_time_result += district_deal_time
    return deal_time_result


#  按年度,季度进行超48小时工单占比统计
def collect_over_48h_rate(statistics_type, year, quarter=1, month=1, day=1, begin_datetime='', end_datetime=''):
    # 构建dict
    over_48h_rate_dict = {}
    over_48h_rate_list = []
    try:
        prd_1_rate = get_district_over_48h_rate(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        over_48h_rate_list += prd_1_rate

        over_48h_rate_dict['result'] = over_48h_rate_list
        over_48h_rate_dict['status'] = 'success'
        return over_48h_rate_dict
    except Exception as e:
        over_48h_rate_dict['msg'] = str(e)
        over_48h_rate_dict['status'] = 'fail'
        return over_48h_rate_dict


# 珠1:1,珠2:2,粤东:3,粤西:4,粤北:5
def get_district_over_48h_rate(statistics_type, year, quarter, month, day, begin_datetime, end_datetime):
    over_result = []
    if 1:
        qs = []
        over_48h_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime),
                                                           processTime__gt='2880').values(
            'city').annotate(over_48h_amount=Count('city'))
        order_amount_queryset = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values(
            'city').annotate(order_amount=Count('city'))
    for district in District.objects.all():
        area = district.district
        cities = get_cities_by_district_id(district.id)
        over_48h_rate_list = []
        for i in cities:
            over_48h_rate_item = dict()
            over_48h_rate_item['area'] = area
            over_48h_rate_item['city'] = i
            if qs and statistics_type != 5:
                city_qs = qs.filter(city=i)
                over_48h_rate_item['Over48Rate'] = city_qs[0].result if city_qs else 0
                over_48h_rate_list.append(over_48h_rate_item)
            elif over_48h_queryset and order_amount_queryset and statistics_type == 5:
                over_48_amount = over_48h_queryset.filter(city=i)[0].get('over_48h_amount', 0) if over_48h_queryset.filter(city=i) else 0
                order_amount = order_amount_queryset.filter(city=i)[0].get('order_amount')
                over_48h_rate_item['Over48Rate'] = round(over_48_amount / order_amount * 100, 2) if order_amount != 0 else 0
                over_48h_rate_list.append(over_48h_rate_item)

            else:
                raise Exception("数据库中无相关数据，时间区间：%s-%s ;类型：%s，;"
                                "%s-%s-%s 季度：%s" % (begin_datetime, end_datetime, statistics_type, year, month, day, quarter))
        district_over_48h_rate = sorted(over_48h_rate_list, key=operator.itemgetter('Over48Rate'), reverse=True)
        for i in district_over_48h_rate:
            i['Over48Rate'] = str(i.get('Over48Rate'))
        over_result += district_over_48h_rate
    return over_result


def collect_deal_quality(statistics_type, year=2018, quarter=1, month=1, day=1, begin_datetime="", end_datetime=""):
    result_list = []
    result = dict()
    # try:
    intime_rate_result = collect_deal_in_time_rate(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
    deal_time_result = collect_deal_time(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
    ovre48_rate_result = collect_over_48h_rate(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
    sign_rate_result = StatisticsQuarterlyQuality.objects.filter(beginDate=begin_datetime, endDate=end_datetime)
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
            for sign_rate_item in sign_rate_result:
                if sign_rate_item.city == city:
                    result_item['SignRate'] = str(sign_rate_item.SignRate) if sign_rate_item.SignRate else ''
            result_list.append(result_item)

    result['status'] = "success"
    result['result'] = result_list
    return result
    # except Exception as e:
    result['status'] = "fail"
    result['msg'] = str(e)
    return result


def collect_specific_dealtime_amount(statistics_type, year=1, quarter=1, month=1, day=1, begin_datetime="", end_datetime=""):
    result_dict = {}
    try:
        result_dict['result'] = get_specific_dealtime_amount(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        result_dict['status'] = 'success'
        return result_dict
    except Exception as e:
        result_dict['status'] = 'fail'
        result_dict['msg'] = str(e)


def get_specific_dealtime_amount(statistics_type, year, quarter, month, day, begin_datetime, end_datetime):
    result_list = []

    if 1:
        qs = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime)).values('city',
                                                                                                         'malfunctionJudgment', 'processTime')
        for district_id in range(1, 6):
            cities = get_cities_by_district_id(district_id)
            for city in cities:
                result_item = dict()
                city_qs = qs.filter(city=city)
                result_item['area'] = District.objects.get(id=district_id).district
                result_item['city'] = city
                line_qs = city_qs.filter(malfunctionJudgment__contains='线路故障').values('city').annotate(sum_dealtime=Sum('processTime'),
                                                                                                       sum_amount=Count('city'))[0]
                line_dealtime = line_qs.get('sum_dealtime', 0)
                line_amount = line_qs.get('sum_amount', 0)
                result_item['line_time'] = str(round(line_dealtime / line_amount / 60, 2) if line_amount != 0 else 0)
                result_item['line_amount'] = str(line_amount)

                equipment_qs = city_qs.filter(malfunctionJudgment__contains='设备故障').values('city').annotate(sum_dealtime=Sum('processTime'),
                                                                                                            sum_amount=Count('city'))[0]
                equipment_dealtime = equipment_qs.get('sum_dealtime', 0)
                equipment_amount = equipment_qs.get('sum_amount', 0)
                result_item['equipment_time'] = str(round(equipment_dealtime / equipment_amount / 60, 2) if equipment_amount != 0 else 0)
                result_item['equipment_amount'] = str(equipment_amount)

                environment_qs = \
                    city_qs.filter(malfunctionJudgment__contains='动环故障').exclude(malfunctionJudgment__contains='停电').values('city').annotate(
                        sum_dealtime=Sum('processTime'), sum_amount=Count('city'))[0]
                environment_dealtime = environment_qs.get('sum_dealtime', 0)
                environment_amount = environment_qs.get('sum_amount', 0)
                result_item['environment_time'] = str(round(environment_dealtime / environment_amount / 60, 2) if environment_amount != 0 else 0)
                result_item['environment_amount'] = str(environment_amount)

                power_qs = \
                    city_qs.filter(malfunctionJudgment__contains='停电').values('city').annotate(sum_dealtime=Sum('processTime'),
                                                                                               sum_amount=Count('city'))[
                        0]
                power_dealtime = power_qs.get('sum_dealtime', 0)
                power_amount = power_qs.get('sum_amount', 0)
                result_item['power_time'] = str(round(power_dealtime / power_amount / 60, 2) if power_amount != 0 else 0)
                result_item['power_amount'] = str(power_amount)
                other_qs = city_qs.exclude(malfunctionJudgment__contains='线路故障').exclude(malfunctionJudgment__contains='设备故障').exclude(
                    malfunctionJudgment__contains='动环故障').values('city').annotate(sum_dealtime=Sum('processTime'), sum_amount=Count('city'))[0]

                other_dealtime = other_qs.get('sum_dealtime', 0)
                other_amount = other_qs.get('sum_amount', 0)
                result_item['other_time'] = str(round(other_dealtime / other_amount / 60, 2) if other_amount != 0 else 0)
                result_item['other_amount'] = str(other_amount)

                result_list.append(result_item)
        return result_list
