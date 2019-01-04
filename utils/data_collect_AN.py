#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
__author__ = silenthz 
__date__ = 2018/9/12
"""

import sys
import os

pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd + "../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DataEcharts.settings")

import django

django.setup()

from django.db.models import Count, Q
from report.models import MalfunctionData
from datetime import timedelta, datetime


def get_top10_ne(begin_datetime, end_datetime, profession):
    qs = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime),
                                        originProfession=profession,
                                        malfunctionSource='集中告警系统报故障',
                                        type='处理',
                                        ne__isnull=False) \
        .exclude(ne='') \
        .values('city', 'ne') \
        .annotate(distributeAmount=Count('ne')) \
        .order_by('distributeAmount') \
        .reverse()
    rs_list = []
    last_amount = 0
    index = 0
    for q in qs:
        if q.get('distributeAmount', '') == last_amount or len(rs_list) < 10:

            if q.get('distributeAmount', '') != last_amount:
                index += 1
            item = dict(
                index=index,
                city=q.get('city', ''),
                ne=q.get('ne', ''),
                distributeAmount=str(q.get('distributeAmount'))
            )
            last_amount = q.get('distributeAmount')
            rs_list.append(item)
        else:
            break
    rs_dict = {profession: rs_list}

    return rs_dict


# 故障总量分布-对比上个月
def get_sum_amount(begin_datetime, end_datetime, city):
    # begin_datetime = datetime.strptime(begin_datetime, '%Y-%m-%d')
    # end_datetime = datetime.strptime(end_datetime, '%Y-%m-%d')
    end_datetime_lm = begin_datetime - timedelta(seconds=1)
    begin_datetime_lm = (begin_datetime - timedelta(days=1)).replace(day=1)
    # print(begin_datetime_lm)
    # print(end_datetime_lm)
    sum_amount = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime), city=city).count()
    sum_amount_lm = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime_lm, end_datetime_lm), city=city).count()
    rs_dict = dict(city=city,
                   sum_amount=str(sum_amount),
                   sum_amount_lm=str(sum_amount_lm))
    return rs_dict


# 故障原因
def get_district_malfunction_reason(begin_date, end_date):
    malfunction_reason = MalfunctionData.objects.filter(distributeTime__range=(begin_date, end_date)) \
        .values_list('district__district', 'sortedReason') \
        .annotate(sum_amount=Count('city'))
    item_1 = dict(profession='其他')
    item_2 = dict(profession='配置')
    item_3 = dict(profession='设备')
    item_4 = dict(profession='线路')
    item_5 = dict(profession='动环及配套')
    item_list = []
    item_list += [item_1, item_2, item_3, item_4, item_5]
    for i in range(1, 6):
        for reason in malfunction_reason:
            if reason[1] == i:
                if reason[0] == '珠1':
                    item_list[i - 1].update({'PRD_1': str(reason[2])})
                if reason[0] == '珠2':
                    item_list[i - 1].update({'PRD_2': str(reason[2])})
                if reason[0] == '粤东':
                    item_list[i - 1].update({'GD_E': str(reason[2])})
                if reason[0] == '粤西':
                    item_list[i - 1].update({'GD_W': str(reason[2])})
                if reason[0] == '粤北':
                    item_list[i - 1].update({'GD_N': str(reason[2])})
    return item_list


from django.db import connection


def get_worst10_department(begin_datetime, end_datetime):
    with connection.cursor() as cursor:
        rs = cursor.execute("""SELECT T1.dutyDepartment,ROUND( T1.co / T2.totalCo * 100, 2 ) inTimeRate,T1.co  inTimeAmount ,T2.totalCo
                          FROM 
                          ( SELECT dutyDepartment, COUNT( * ) co FROM report_malfunction_data WHERE isTimeOut = '否' AND distributeTime BETWEEN %s AND %s GROUP BY dutyDepartment ) T1,
                          ( SELECT dutyDepartment, COUNT( * ) totalCo FROM report_malfunction_data WHERE distributeTime BETWEEN %s AND %s GROUP BY dutyDepartment ) T2
                          WHERE T1.dutyDepartment = T2.dutyDepartment
                          ORDER BY inTimeRate,inTimeAmount DESC """,
                            [begin_datetime, end_datetime, begin_datetime, end_datetime])
        rows = cursor.fetchall()
    result_list = []
    for row in rows:
        d = dict()
        d['department'] = str(row[0])
        d['total_amount'] = str(row[3])
        d['intime_amount'] = str(row[2])
        d['timeout_admount'] = str(row[3] - row[2])
        d['intime_rate'] = str(row[1])
        if row[3] - row[2] >= 30:
            result_list.append(d)
            if len(result_list) == 10:
                return result_list
    return result_list
