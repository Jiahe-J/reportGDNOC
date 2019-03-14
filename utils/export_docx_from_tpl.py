#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
__author__ = silenthz 
__date__ = 2018/11/21
"""
# import os
#
# import sys
#
# pwd = os.path.dirname(os.path.realpath(__file__))
# # 将项目目录加入setting
# sys.path.append(pwd + "../")
# # manage.py中
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DataEcharts.settings")
#
# import django
#
# django.setup()

from django.forms import model_to_dict
from docxtpl import DocxTemplate

from report.models import StatisticsTop10Ne, StatisticsMonthlyWorst10Department, StatisticsQuarterlyAmount, StatisticsQuarterlyQuality, \
    StatisticsQuarterlySpecificDealtimeAmount
from utils.data_collect_weekly import collect_track_weekly, collect_longtime_weekly


def monthly_export_docx(year, month):
    filename = 'monthly' + str(year) + '-' + str(month) + '.docx'
    filepath = 'utils/export_docx/' + filename

    tpl = DocxTemplate('utils/export_docx/template/monthly_tpl.docx')
    context = dict()

    i = 0
    context['G4_Repeater'] = []
    qs_Net_4G = StatisticsTop10Ne.objects.filter(yearNum=year, monthNum=month, profession='Net_4G')
    qs_Repeater = StatisticsTop10Ne.objects.filter(yearNum=year, monthNum=month, profession='Repeater')

    for q in qs_Net_4G:
        d = dict()
        q_dict = model_to_dict(q, exclude=['id', 'yearNum', 'monthNum', 'profession'])
        for k in q_dict:
            new_k = k + '_' + 'Net_4G'
            d[new_k] = q_dict[k]
        context['G4_Repeater'].append(d)
    for q in qs_Repeater:
        q_dict = model_to_dict(q, exclude=['id', 'yearNum', 'monthNum', 'profession'])
        d = dict()
        for k in q_dict:
            new_k = k + '_' + 'Repeater'
            d[new_k] = q_dict[k]
        if i < len(context['G4_Repeater']):
            context['G4_Repeater'][i].update(d)
            i += 1
        else:
            context['G4_Repeater'].append(d)

    i = 0
    context['CDMA_Transmission'] = []
    qs_Net_CDMA = StatisticsTop10Ne.objects.filter(yearNum=year, monthNum=month, profession='Net_CDMA')
    qs_Transmission = StatisticsTop10Ne.objects.filter(yearNum=year, monthNum=month, profession='Transmission')
    for q in qs_Net_CDMA:
        q_dict = model_to_dict(q, exclude=['id', 'yearNum', 'monthNum', 'profession'])
        d = dict()
        for k in q_dict:
            new_k = k + '_' + 'Net_CDMA'
            d[new_k] = q_dict[k]
        context['CDMA_Transmission'].append(d)

    for q in qs_Transmission:
        q_dict = model_to_dict(q, exclude=['id', 'yearNum', 'monthNum', 'profession'])
        d = dict()
        for k in q_dict:
            new_k = k + '_' + 'Transmission'
            d[new_k] = q_dict[k]
        if i < len(context['CDMA_Transmission']):
            context['CDMA_Transmission'][i].update(d)
            i += 1
        else:
            context['CDMA_Transmission'].append(d)

    i = 0
    context['Optical_Dynamics'] = []
    qs_Net_Optical = StatisticsTop10Ne.objects.filter(yearNum=year, monthNum=month, profession='Net_Optical')
    qs_Dynamics = StatisticsTop10Ne.objects.filter(yearNum=year, monthNum=month, profession='Dynamics')
    for q in qs_Net_Optical:
        q_dict = model_to_dict(q, exclude=['id', 'yearNum', 'monthNum', 'profession'])
        d = dict()
        for k in q_dict:
            new_k = k + '_' + 'Net_Optical'
            d[new_k] = q_dict[k]
        context['Optical_Dynamics'].append(d)

    for q in qs_Dynamics:
        q_dict = model_to_dict(q, exclude=['id', 'yearNum', 'monthNum', 'profession'])
        d = dict()
        for k in q_dict:
            new_k = k + '_' + 'Dynamics'
            d[new_k] = q_dict[k]
        if i < len(context['Optical_Dynamics']):
            context['Optical_Dynamics'][i].update(d)
            i += 1
        else:
            context['Optical_Dynamics'].append(d)

    i = 0
    context['Exchange_Data'] = []
    qs_Exchange = StatisticsTop10Ne.objects.filter(yearNum=year, monthNum=month, profession='Exchange')
    qs_Data = StatisticsTop10Ne.objects.filter(yearNum=year, monthNum=month, profession='Data')
    for q in qs_Exchange:
        q_dict = model_to_dict(q, exclude=['id', 'yearNum', 'monthNum', 'profession'])
        d = dict()
        for k in q_dict:
            new_k = k + '_' + 'Exchange'
            d[new_k] = q_dict[k]
        context['Exchange_Data'].append(d)

    for q in qs_Data:
        q_dict = model_to_dict(q, exclude=['id', 'yearNum', 'monthNum', 'profession'])
        d = dict()
        for k in q_dict:
            new_k = k + '_' + 'Data'
            d[new_k] = q_dict[k]
        if i < len(context['Exchange_Data']):
            context['Exchange_Data'][i].update(d)
            i += 1
        else:
            context['Exchange_Data'].append(d)

    # 五、处理及时率差的部门
    context['departments'] = []
    qs = StatisticsMonthlyWorst10Department.objects.filter(yearNum=year, monthNum=month)
    for q in qs:
        context['departments'].append(model_to_dict(q, exclude=['id', 'yearNum', 'monthNum']))

    # 图片替换
    tpl.replace_pic('amount_compare.png', 'utils/export_docx/image/monthly_amount_' + str(year) + '_' + str(month) + '.png')
    tpl.replace_pic('district_reason.png', 'utils/export_docx/image/monthly_reason_' + str(year) + '_' + str(month) + '.png')
    tpl.replace_pic('city_rate.png', 'utils/export_docx/image/monthly_quality_' + str(year) + '_' + str(month) + '.png')

    tpl.render(context)
    tpl.save(filepath)
    # print(context)

    return filepath, filename


def quarterly_export_docx(beginDate, endDate):
    filename = 'quarterly' + '_' + beginDate + '_' + endDate + '.docx'
    filepath = 'utils/export_docx/' + filename
    tpl = DocxTemplate('utils/export_docx/template/quarterly_tpl.docx')
    context = dict()
    area_list = ['珠1', '珠2', '粤东', '粤西', '粤北']
    index = 1
    total_transmission = 0
    total_dynamics = 0
    total_exchange = 0
    total_AN = 0
    total_wireless = 0

    sum_signRate = 0
    sum_intimeRate = 0
    sum_dealTime = 0
    sum_over48Rate = 0

    sum_line = 0
    sum_power = 0
    sum_equipment = 0
    sum_environment = 0
    sum_other = 0

    avg_line = 0
    avg_power = 0
    avg_equipment = 0
    avg_environment = 0
    avg_other = 0
    for area in area_list:
        context['AmountArea' + str(index)] = []
        context['QualityArea' + str(index)] = []
        context['SpecificDealtimeAmount' + str(index)] = []
        context['district' + str(index)] = area
        qs_amount = StatisticsQuarterlyAmount.objects.filter(beginDate=beginDate, endDate=endDate, area=area)
        qs_quality = StatisticsQuarterlyQuality.objects.filter(beginDate=beginDate, endDate=endDate, area=area)
        qs_specific = StatisticsQuarterlySpecificDealtimeAmount.objects.filter(beginDate=beginDate, endDate=endDate, area=area)
        for q in qs_amount:
            q_dict = model_to_dict(q, exclude=['id', 'beginDate', 'endDate'])
            context['AmountArea' + str(index)].append(q_dict)
            total_transmission += q_dict.get('transmission', 0)
            total_dynamics += q_dict.get('dynamics', 0)
            total_exchange += q_dict.get('exchange', 0)
            total_AN += q_dict.get('AN', 0)
            total_wireless += q_dict.get('wireless', 0)

        for q in qs_quality:
            q_dict = model_to_dict(q, exclude=['id', 'beginDate', 'endDate'])
            context['QualityArea' + str(index)].append(q_dict)
            sum_signRate += q_dict.get('SignRate', 0)
            sum_intimeRate += q_dict.get('IntimeRate', 0)
            sum_dealTime += q_dict.get('AverageTime', 0)
            sum_over48Rate += q_dict.get('Over48Rate', 0)

        for q in qs_specific:
            q_dict = model_to_dict(q, exclude=['id', 'beginDate', 'endDate'])
            context['SpecificDealtimeAmount' + str(index)].append(q_dict)

            sum_line += q_dict.get('line_amount', 0)
            sum_power += q_dict.get('power_amount', 0)
            sum_equipment += q_dict.get('equipment_amount', 0)
            sum_environment += q_dict.get('environment_amount', 0)
            sum_other += q_dict.get('other_amount', 0)
            avg_line += q_dict.get('line_time', 0)
            avg_power += q_dict.get('power_time', 0)
            avg_equipment += q_dict.get('equipment_time', 0)
            avg_environment += q_dict.get('environment_time', 0)
            avg_other += q_dict.get('other_time', 0)
        index += 1
    context['total_transmission'] = total_transmission
    context['total_dynamics'] = total_dynamics
    context['total_exchange'] = total_exchange
    context['total_AN'] = total_AN
    context['total_wireless'] = total_wireless
    context['total'] = total_transmission + total_dynamics + total_exchange + total_AN + total_wireless

    context['avg_signRate'] = round(sum_signRate / 21, 2)
    context['avg_intimeRate'] = round(sum_intimeRate / 21, 2)
    context['avg_dealTime'] = round(sum_dealTime / 21, 2)
    context['avg_over48Rate'] = round(sum_over48Rate / 21, 2)

    context['sum_line'] = sum_line
    context['sum_power'] = sum_power
    context['sum_equipment'] = sum_equipment
    context['sum_environment'] = sum_environment
    context['sum_other'] = sum_other
    context['avg_line'] = round(avg_line / 21, 2)
    context['avg_power'] = round(avg_power / 21, 2)
    context['avg_equipment'] = round(avg_equipment / 21, 2)
    context['avg_environment'] = round(avg_environment / 21, 2)
    context['avg_other'] = round(avg_other / 21, 2)

    # 图片替换
    tpl.replace_pic('quarterly_amount.png', 'utils/export_docx/image/quarterly_amount_' + beginDate + '_' + endDate + '.png')
    tpl.replace_pic('quarterly_intime.png', 'utils/export_docx/image/quarterly_intime_' + beginDate + '_' + endDate + '.png')
    tpl.replace_pic('quarterly_dealtime.png', 'utils/export_docx/image/quarterly_dealtime_' + beginDate + '_' + endDate + '.png')
    tpl.replace_pic('quarterly_over48.png', 'utils/export_docx/image/quarterly_over48_' + beginDate + '_' + endDate + '.png')
    tpl.replace_pic('quarterly_reason_amount.png', 'utils/export_docx/image/quarterly_reason_amount_' + beginDate + '_' + endDate + '.png')
    tpl.replace_pic('quarterly_specific_amount.png', 'utils/export_docx/image/quarterly_specific_amount_' + beginDate + '_' + endDate + '.png')
    tpl.replace_pic('quarterly_specific_dealtime.png', 'utils/export_docx/image/quarterly_specific_dealtime_' + beginDate + '_' + endDate + '.png')

    # print(context)
    tpl.render(context)
    tpl.save(filepath)

    return filepath, filename


def weekly_export_docx(beginDate, endDate):
    filename = 'weekly' + '_' + beginDate + '_' + endDate + '.docx'
    filepath = 'utils/export_docx/' + filename
    tpl = DocxTemplate('utils/export_docx/template/weekly_tpl.docx')
    context = dict()
    track_list = collect_track_weekly(beginDate, endDate)
    longtiem_list = collect_longtime_weekly()
    context['weeklyTrack'] = track_list
    context['weeklyLongtime'] = longtiem_list
    # 图片替换
    tpl.replace_pic('weekly_track.png', 'utils/export_docx/image/weekly_track_' + beginDate + '_' + endDate + '.png')
    tpl.replace_pic('weekly_longtime.png', 'utils/export_docx/image/weekly_longtime_' + beginDate + '_' + endDate + '.png')

    tpl.render(context)
    tpl.save(filepath)
    return filepath, filename
