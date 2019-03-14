#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
__author__ = silenthz 
__date__ = 2019/3/14
"""
from report.models import StatisticsTop10Ne, StatisticsMonthlyWorst10Department


def removeTop10Ne(year, month):
    StatisticsTop10Ne.objects.filter(yearNum=int(year), monthNum=int(month)).delete()
    return '%s-%s Top10Ne删除成功' % (year, month) + ';\n'


def removeWorst10department(year, month):
    StatisticsMonthlyWorst10Department.objects.filter(yearNum=int(year), monthNum=int(month)).delete()
    return '%s-%s Worst10Department删除成功' % (year, month) + ';\n'
