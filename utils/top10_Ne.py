#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
__author__ = silenthz 
__date__ = 2018/9/12
"""

# import sys
# import os
#
# pwd = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(pwd + "../")
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DataEcharts.settings")
#
# import django
#
# django.setup()

from django.db.models import Count, Q
from report.models import MalfunctionData


def get_top10_ne(begin_datetime, end_datetime, profession):
    qs = MalfunctionData.objects.filter(distributeTime__range=(begin_datetime, end_datetime),
                                        profession=profession,
                                        malfunctionSource='集中告警系统报故障',
                                        type='处理',
                                        ne__isnull=False) \
             .values('city', 'ne') \
             .annotate(distributeAmount=Count('ne')) \
             .order_by('distributeAmount') \
             .reverse()[:10]
    rs_list = []
    for q in qs:
        item = dict(
            city=q.get('city', ''),
            ne=q.get('ne', ''),
            distributeAmount=str(q.get('distributeAmount'))
        )
        rs_list.append(item)
    rs_dict = {profession: rs_list}

    return rs_dict


# begin_datetime = '2018-01-01'
# end_datetime = '2018-01-31'
#
# profession_list = ['4G网络', '直放站', 'CDMA网络', '本地传输', '光网络', '动力', '交换接入网', '数据']
# rs_dict = dict()
# for profession in profession_list:
#     rs_dict.update(get_top10_ne(begin_datetime, end_datetime, profession))


# qs = MalfunctionData.objects.filter(Q(category__contains='本地传输') | Q(category__contains='本地光缆'))
# for q in qs:
#     q.profession = '本地传输'
#     q.save()
