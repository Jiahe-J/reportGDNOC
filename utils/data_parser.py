#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
@author:silenthz 
@file: data_parser.py
@time: 2018/06/06
@报表解析工具库
"""

# 处理及时率示例
import calendar
import datetime
import xlrd
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from openpyxl import load_workbook

from report.models import MalfunctionData


def deal_in_time_rate_parser():
    # 解析报表文件为元组,分组,排序
    dict = {'广州': 99, '深圳': 98, '东莞': 97, '佛山': 100, '珠海': 88, '中山': 95, '惠州': 87, '江门': 85}
    sortedTuple = sorted(dict.items(), key=lambda x: x[1], reverse=True)
    cities = []
    rate = []
    for item in sortedTuple:
        cities.append(item[0])
        rate.append(item[1])
    return cities, rate


# 按季度删除原有数据
def delete_former_data(year, quarter):
    year = int(year)
    quarter = int(quarter)
    if quarter >= 1 and quarter <= 4:
        begin_datetime = datetime.date(year, quarter, 1)
        end_datetime = datetime.date(year, quarter * 3, calendar.mdays[quarter * 3])
        MalfunctionData.objects.filter(distributeTime__gte=begin_datetime, distributeTime__lte=end_datetime).delete()


# 批量导入excel .xls数据
def parse_malfunction_data_xls(filename=None, file_contents=None, has_repeat_data=False):
    if filename:
        workbook = xlrd.open_workbook(filename)
    else:
        workbook = xlrd.open_workbook(file_contents=file_contents)
    sheet = workbook.sheet_by_index(0)
    # 数据行数
    nrows = sheet.nrows

    malfunctionList = []

    for i in range(1, nrows):
        malfunctionData = MalfunctionData()
        malfunctionData.city = sheet.cell_value(i, 1)
        malfunctionData.profession = sheet.cell_value(i, 2)
        malfunctionData.department = sheet.cell_value(i, 3)
        malfunctionData.malfunctionCity = sheet.cell_value(i, 4)
        malfunctionData.receiptNumber = sheet.cell_value(i, 5)
        malfunctionData.receiptSerialNumber = sheet.cell_value(i, 6)
        malfunctionData.receiptStatus = sheet.cell_value(i, 7)
        malfunctionData.title = sheet.cell_value(i, 8)
        malfunctionData.category = sheet.cell_value(i, 9)
        malfunctionData.distributeTime = datetime.datetime.strptime(sheet.cell_value(i, 10), '%Y-%m-%d %H:%M:%S')
        processTime = sheet.cell_value(i, 11)
        malfunctionData.processTime = processTime if processTime else 0
        hangTime = sheet.cell_value(i, 12)
        malfunctionData.hangTime = hangTime if hangTime else 0
        malfunctionData.malfunctionSource = sheet.cell_value(i, 13)
        malfunctionData.isTimeOut = sheet.cell_value(i, 14)
        malfunctionData.dutyDepartment = sheet.cell_value(i, 15)
        malfunctionData.conclusion = sheet.cell_value(i, 16)
        malfunctionData.type = sheet.cell_value(i, 17)
        malfunctionData.reasonClassification = sheet.cell_value(i, 18)
        malfunctionData.malfunctionJudgment = sheet.cell_value(i, 19)
        malfunctionData.malfunctionReason = sheet.cell_value(i, 20)
        malfunctionData.originProfession = sheet.cell_value(i, 21)
        # 解决导入重复数据,但插入速度慢
        if has_repeat_data:
            try:
                MalfunctionData.objects.get(receiptNumber=sheet.cell_value(i, 5))
                malfunctionData.save()
            except ObjectDoesNotExist:
                malfunctionList.append(malfunctionData)
        else:
            malfunctionList.append(malfunctionData)
        if (len(malfunctionList) == 500):
            try:
                MalfunctionData.objects.bulk_create(malfunctionList)
                malfunctionList = []
            except IntegrityError:
                status = '有重复数据,请选择"替换导入"方式'
                return status
    MalfunctionData.objects.bulk_create(malfunctionList)


# 批量导入excel .xlsx数据
def parse_malfunction_data_xlsx(filename=None, has_repeat_data=False):
    if filename:
        workbook = load_workbook(filename, read_only=True)
    else:
        return {'status': 'fail'}

    sheet = workbook[workbook.sheetnames[0]]
    # 数据行数
    # nrows = sheet.nrows

    malfunctionList = []
    rows = sheet.rows
    rows.__next__()
    for row in rows:
        malfunctionData = MalfunctionData()
        malfunctionData.city = row[1].value
        malfunctionData.profession = row[2].value
        malfunctionData.department = row[3].value
        malfunctionData.malfunctionCity = row[4].value
        malfunctionData.receiptNumber = row[5].value
        malfunctionData.receiptSerialNumber = row[6].value
        malfunctionData.receiptStatus = row[7].value
        malfunctionData.title = row[8].value
        malfunctionData.category = row[9].value
        malfunctionData.distributeTime = datetime.datetime.strptime(row[10].value, '%Y-%m-%d %H:%M:%S')
        processTime = row[11].value
        malfunctionData.processTime = processTime if processTime else 0
        hangTime = row[12].value
        malfunctionData.hangTime = hangTime if hangTime else 0
        malfunctionData.malfunctionSource = row[13].value
        malfunctionData.isTimeOut = row[14].value
        malfunctionData.dutyDepartment = row[15].value
        malfunctionData.conclusion = row[16].value
        malfunctionData.type = row[17].value
        malfunctionData.reasonClassification = row[18].value
        malfunctionData.malfunctionJudgment = row[19].value
        malfunctionData.malfunctionReason = row[20].value
        malfunctionData.originProfession = row[21].value
        # 解决导入重复数据,但插入速度慢
        if has_repeat_data:
            try:
                MalfunctionData.objects.get(receiptNumber=row[5].value)
                malfunctionData.save()
            except ObjectDoesNotExist:
                malfunctionList.append(malfunctionData)
        else:
            malfunctionList.append(malfunctionData)

        if (len(malfunctionList) == 2000):
            try:
                MalfunctionData.objects.bulk_create(malfunctionList)
                malfunctionList = []
            except IntegrityError:
                status = '有重复数据,请选择"替换导入"方式'
                return status
    MalfunctionData.objects.bulk_create(malfunctionList)
