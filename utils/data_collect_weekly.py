#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
__author__ = silenthz 
__date__ = 2018/10/23
"""
import datetime

from django.db.models import Count

from report.models import MalfunctionLongtime, MalfunctionOnTrack, City


def collect_longtime_weekly():
    m1 = MalfunctionLongtime.objects.all().values('city').annotate(sum_amount=Count('city'))
    m2 = MalfunctionLongtime.objects.filter(processTime__range=(4320, 10080)).values('city').annotate(amount_3_7=Count('city'))
    m3 = MalfunctionLongtime.objects.filter(processTime__gt=10080).values('city').annotate(amount_over_7=Count('city'))

    dict_m1 = dict()
    dict_m2 = dict()
    dict_m3 = dict()

    for i in m1:
        if i.get('city'):
            dict_m1[i.get('city')] = i.get('sum_amount')

    for i in m2:
        if i.get('city'):
            dict_m2[i.get('city')] = i.get('amount_3_7')

    for i in m3:
        if i.get('city'):
            dict_m3[i.get('city')] = i.get('amount_over_7')

    city_list = ['省公司']
    cities = City.objects.values('city')
    for city in cities:
        city_list.append(city.get('city'))

    rs_list = []
    total_amount = 0
    total_3_7 = 0
    total_over_7 = 0
    for city in city_list:
        sum_amount = dict_m1.get(city, 0)
        total_amount += sum_amount
        amount_3_7 = dict_m2.get(city, 0)
        total_3_7 += amount_3_7
        amount_over_7 = dict_m3.get(city, 0)
        total_over_7 += amount_over_7
        item = dict(city=city,
                    sum_amount=str(sum_amount),
                    amount_3_7=str(amount_3_7),
                    amount_3_7_rate=str(round(amount_3_7 / sum_amount * 100, 2)) if sum_amount else '0',
                    amount_over_7=str(amount_over_7),
                    amount_over_7_rate=str(round(amount_over_7 / sum_amount * 100, 2)) if sum_amount else '0')
        rs_list.append(item)
    item = dict(city='合计',
                sum_amount=str(total_amount),
                amount_3_7=str(total_3_7),
                amount_3_7_rate=str(round(total_3_7 / total_amount * 100, 2)),
                amount_over_7=str(total_over_7),
                amount_over_7_rate=str(round(total_over_7 / total_amount * 100, 2)))
    rs_list.append(item)
    return rs_list


def collect_track_weekly(begin_date, end_date):
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1)
    month_list = list(range(1, 13))
    year = end_date.year
    month = end_date.month
    last_month = month_list[month_list.index(month) - 1]
    last_3month = month_list[month_list.index(month) - 3]
    last_month_year = year if last_month < month else year - 1
    last_3month_year = year if last_3month < month else year - 1

    last_month_date = end_date.replace(year=last_month_year, month=last_month)
    last_3month_date = end_date.replace(year=last_3month_year, month=last_3month)

    # 在途遗留跟踪单,故障状态不为“已归档????
    m1 = MalfunctionOnTrack.objects.exclude(receiptStatus='已归档').values('city').annotate(sum_amount=Count('city'))
    # 本周新增
    m2 = MalfunctionOnTrack.objects.filter(createTime__range=(begin_date, end_date)) \
        .exclude(receiptStatus='已归档').values('city') \
        .annotate(new_amount=Count('city'))
    # 本周完成
    m3 = MalfunctionOnTrack.objects.filter(receiptStatus='已归档').values('city').annotate(finish_amount=Count('city'))
    # 处理时间超一个月
    m4 = MalfunctionOnTrack.objects.filter(createTime__lte=last_month_date) \
        .exclude(receiptStatus='已归档').values('city') \
        .annotate(over1__amount=Count('city'))
    # 处理时间超三个月
    m5 = MalfunctionOnTrack.objects.filter(createTime__lte=last_3month_date) \
        .exclude(receiptStatus='已归档').values('city') \
        .annotate(over3__amount=Count('city'))

    dict_m1 = dict()
    dict_m2 = dict()
    dict_m3 = dict()
    dict_m4 = dict()
    dict_m5 = dict()
    for i in m1:
        if i.get('city'):
            dict_m1[i.get('city')] = i.get('sum_amount')

    for i in m2:
        if i.get('city'):
            dict_m2[i.get('city')] = i.get('new_amount')

    for i in m3:
        if i.get('city'):
            dict_m3[i.get('city')] = i.get('finish_amount')

    for i in m4:
        if i.get('city'):
            dict_m4[i.get('city')] = i.get('over1__amount')

    for i in m5:
        if i.get('city'):
            dict_m5[i.get('city')] = i.get('over3__amount')

    city_list = ['省公司']
    cities = City.objects.values('city')
    for city in cities:
        city_list.append(city.get('city'))

    rs_list = []
    total_amount = 0
    total_new = 0
    total_finish = 0
    total_over1 = 0
    total_over3 = 0

    for city in city_list:
        sum_amount = dict_m1.get(city, 0)
        total_amount += sum_amount
        new_amount = dict_m2.get(city, 0)
        total_new += new_amount
        finish_amount = dict_m3.get(city, 0)
        total_finish += finish_amount
        over1_amount = dict_m4.get(city, 0)
        total_over1 += over1_amount
        over3_amount = dict_m5.get(city, 0)
        total_over3 += over3_amount
        item = dict(city=city,
                    sum_amount=str(sum_amount),
                    new_amount=str(new_amount),
                    new_rate=str(round(new_amount / sum_amount * 100, 2)) if sum_amount else '0',
                    finish_amount=str(finish_amount),
                    finish_rate=str(round(finish_amount / (sum_amount + finish_amount) * 100, 2)) if sum_amount else '0',
                    over1_amount=str(over1_amount),
                    over3_amount=str(over3_amount))

        rs_list.append(item)
    item = dict(city='合计',
                sum_amount=str(total_amount),
                new_amount=str(total_new),
                new_rate=str(round(total_new / total_amount * 100, 2)) if total_amount else '0',
                finish_amount=str(total_finish),
                finish_rate=str(round(total_finish / (total_amount + total_finish) * 100, 2)) if total_amount else '0',
                over1_amount=str(total_over1),
                over3_amount=str(total_over3))
    rs_list.append(item)
    return rs_list
