# coding=utf8
import calendar
import datetime

from django.forms import model_to_dict
from django.http import JsonResponse, FileResponse, HttpResponse
from django.shortcuts import render
from django.utils.encoding import escape_uri_path
from django.views.generic.base import View
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from report.models import City, StatisticsMonthlyQuality, StatisticsTop10Ne, StatisticsMonthlyAmount, StatisticsMonthlyReason, \
    StatisticsMonthlyWorst10Department, StatisticsQuarterlyAmount, StatisticsQuarterlyQuality, StatisticsQuarterlySpecificDealtimeAmount
from utils.data_collect import collect_order_amount_table, collect_deal_time, collect_over_48h_rate, \
    collect_deal_in_time_rate, collect_deal_quality, collect_specific_dealtime_amount
from utils.data_collect_AN import get_top10_ne, get_sum_amount, get_district_malfunction_reason, get_worst10_department
from utils.data_collect_weekly import collect_longtime_weekly, collect_track_weekly
from utils.data_parser import parse_indicators_xls, parse_malfunction_data_xlsx, parse_malfunction_longtime, parse_malfunction_track
from utils.decode_base64img import save_base64
from utils.export import export_top10ne
from utils.export_docx_from_tpl import monthly_export_docx, quarterly_export_docx, weekly_export_docx


class OrderAmountView(View):

    def get(self, request, begin_date, end_date):
        print(begin_date, end_date)
        st = datetime.datetime.now()

        qs = StatisticsQuarterlyAmount.objects.filter(beginDate=begin_date, endDate=end_date)
        if qs:
            result_json = dict(result=[])
            for item in qs:
                d = model_to_dict(item)
                d.pop('id'),
                d.pop('beginDate')
                d.pop('endDate')
                for key in d:
                    d[key] = str(d[key])
                result_json['result'].append(d)
                result_json['status'] = 'success'
        else:
            result_json = collect_order_amount_table(5, 2018, 1, 1, 1, begin_date, end_date)
            rs = result_json['result']
            for row in rs:
                StatisticsQuarterlyAmount(beginDate=begin_date, endDate=end_date,
                                          area=row['area'], city=row['city'],
                                          transmission=row['transmission'],
                                          dynamics=row['dynamics'],
                                          exchange=row['exchange'],
                                          AN=row['AN'],
                                          wireless=row['wireless'],
                                          sum=row['sum']).save()
        result_json['process_time'] = str(datetime.datetime.now() - st)
        return JsonResponse(data=result_json, safe=False)


class IntimeRateView(View):
    def get(self, request, begin_date, end_date):
        # print(begin_date, end_date)
        st = datetime.datetime.now()
        result_json = dict()
        try:
            result_json = collect_deal_in_time_rate(5, 2018, 1, 1, 1, begin_date, end_date)
            result_json['process_time'] = str(datetime.datetime.now() - st)
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


class DealtimeView(View):

    def get(self, request, begin_date, end_date):
        # print(begin_date, end_date)
        st = datetime.datetime.now()
        result_json = dict()
        try:
            result_json = collect_deal_time(5, 2018, 1, 1, 1, begin_date, end_date)
            result_json['process_time'] = str(datetime.datetime.now() - st)
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


class Over48RateView(View):

    def get(self, request, begin_date, end_date):
        # print(begin_date, end_date)
        st = datetime.datetime.now()
        result_json = dict()
        try:
            result_json = collect_over_48h_rate(5, 2018, 1, 1, 1, begin_date, end_date)
            result_json['process_time'] = str(datetime.datetime.now() - st)
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


class DealQualityView(View):

    def get(self, request, begin_date, end_date):
        # print(begin_date, end_date)
        st = datetime.datetime.now()
        result_json = dict()
        # try:
        qs = StatisticsQuarterlyQuality.objects.filter(beginDate=begin_date, endDate=end_date, area__isnull=False)
        if qs:
            result_json = dict(result=[])
            for item in qs:
                d = model_to_dict(item)
                d.pop('id'),
                d.pop('beginDate')
                d.pop('endDate')
                for key in d:
                    d[key] = str(d[key])
                result_json['result'].append(d)
                result_json['status'] = 'success'
        else:
            result_json = collect_deal_quality(5, 2018, 1, 1, 1, begin_date, end_date)
            rs = result_json['result']
            for r in rs:
                StatisticsQuarterlyQuality.objects.get_or_create(beginDate=begin_date, endDate=end_date,
                                                                 city=r.get('city', ''))
                StatisticsQuarterlyQuality.objects.filter(beginDate=begin_date, endDate=end_date,
                                                          city=r.get('city', '')) \
                    .update(area=r.get('area'),
                            IntimeRate=float(r.get('IntimeRate', '')),
                            SignRate=float(r.get('SignRate', 0)),
                            Over48Rate=float(r.get('Over48Rate', '')),
                            AverageTime=float(r.get('AverageTime', '')))
                result_json['process_time'] = str(datetime.datetime.now() - st)
        return JsonResponse(data=result_json, safe=False)

        # except Exception as e:
        result_json['status'] = 'fail'
        result_json['msg'] = str(e)
        return JsonResponse(data=result_json, safe=False)


class SpecificDealtimeAmountView(View):

    def get(self, request, begin_date, end_date):
        # print(begin_date, end_date)
        st = datetime.datetime.now()
        result_json = dict()
        try:
            qs = StatisticsQuarterlySpecificDealtimeAmount.objects.filter(beginDate=begin_date, endDate=end_date)
            if qs:
                result_json = dict(result=[])
                for item in qs:
                    d = model_to_dict(item)
                    d.pop('id'),
                    d.pop('beginDate')
                    d.pop('endDate')
                    for key in d:
                        d[key] = str(d[key])
                    result_json['result'].append(d)
                    result_json['status'] = 'success'
            else:
                result_json = collect_specific_dealtime_amount(5, 2018, 1, 1, 1, begin_date, end_date)
                rs = result_json['result']
                for r in rs:
                    StatisticsQuarterlySpecificDealtimeAmount(area=r.get('area', ''), city=r.get('city', ''),
                                                              beginDate=begin_date, endDate=end_date,
                                                              line_time=r.get('line_time', 0),
                                                              line_amount=r.get('line_amount', 0),
                                                              environment_time=r.get('environment_time', 0),
                                                              environment_amount=r.get('environment_amount', 0),
                                                              equipment_time=r.get('equipment_time', 0),
                                                              equipment_amount=r.get('equipment_amount', 0),
                                                              power_time=r.get('power_time', 0),
                                                              power_amount=r.get('power_amount', 0),
                                                              other_time=r.get('other_time', 0),
                                                              other_amount=r.get('other_amount', 0)).save()
            result_json['process_time'] = str(datetime.datetime.now() - st)
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


# 重复派单网元Top10
class Top10NeView(View):

    def get(self, request, year, month):
        begin_date = datetime.date(year, month, 1)
        end_date = datetime.datetime(year, month, calendar.mdays[month], 23, 59, 59)
        # print(begin_date, end_date)
        st = datetime.datetime.now()
        result_json = dict()
        try:
            profession_list = ['Net_4G', 'Repeater', 'Net_CDMA', 'Transmission', 'Net_Optical', 'Dynamics', 'Exchange', 'Data']
            rs_dict = dict()
            qs = StatisticsTop10Ne.objects.filter(yearNum=year, monthNum=month)
            if qs:
                rs_dict = dict()
                for profession in profession_list:
                    rs_dict[profession] = []
                for q in qs:
                    item = dict(index=str(q.index), city=q.city, ne=q.ne, distributeAmount=str(q.amount))
                    rs_dict[q.profession].append(item)

            else:
                for profession in profession_list:
                    rs = get_top10_ne(begin_date, end_date, profession)
                    rs_dict.update(rs)
                    for item in rs[profession]:
                        value_list = list(item.values())
                        StatisticsTop10Ne(index=str(value_list[0]),
                                          city=value_list[1],
                                          ne=value_list[2],
                                          amount=value_list[3],
                                          yearNum=year,
                                          monthNum=month,
                                          profession=profession
                                          ).save()
            result_json['result'] = rs_dict
            result_json['process_time'] = str(datetime.datetime.now() - st)
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


class SumAmountComparedView(APIView):
    # authentication_classes = (SessionAuthentication, BasicAuthentication, JSONWebTokenAuthentication)
    # permission_classes = (IsAuthenticated,)

    def get(self, request, year, month):
        begin_date = datetime.datetime(year, month, 1, 0, 0, 0)
        end_date = datetime.datetime(year, month, calendar.mdays[month], 23, 59, 59)
        # print(begin_date, end_date)
        st = datetime.datetime.now()
        result_json = dict()
        try:
            cities = City.objects.all()
            rs_list = []
            last_month = month - 1 if month - 1 > 0 else 12
            last_year = year if last_month < 12 else year - 1
            qs = StatisticsMonthlyAmount.objects.filter(yearNum=year, monthNum=month)
            qs_lm = StatisticsMonthlyAmount.objects.filter(yearNum=last_year, monthNum=last_month)
            if qs and qs_lm:
                for city in cities:
                    d = dict(city=city.city)
                    for q in qs:
                        if city.city == q.city:
                            d['sum_amount'] = str(q.amount)
                    for q_lm in qs_lm:
                        if city.city == q_lm.city:
                            d['sum_amount_lm'] = str(q_lm.amount)
                    rs_list.append(d)
            else:
                for city in cities:
                    item = get_sum_amount(begin_date, end_date, city.city)
                    rs_list.append(item)
                    if not StatisticsMonthlyAmount.objects.filter(yearNum=year, monthNum=month, city=city.city):
                        StatisticsMonthlyAmount(yearNum=year, monthNum=month, city=city.city,
                                                amount=item['sum_amount']).save()
                    if not StatisticsMonthlyAmount.objects.filter(yearNum=last_year, monthNum=last_month, city=city.city):
                        StatisticsMonthlyAmount(yearNum=last_year, monthNum=last_month, city=city.city,
                                                amount=item['sum_amount_lm']).save()

            result_json['result'] = rs_list
            result_json['process_time'] = str(datetime.datetime.now() - st)
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


class DistrictReasonView(APIView):
    # authentication_classes = (SessionAuthentication, BasicAuthentication, JSONWebTokenAuthentication)
    # permission_classes = (IsAuthenticated,)

    def get(self, request, year, month):
        begin_date = datetime.date(year, month, 1)
        end_date = datetime.datetime(year, month, calendar.mdays[month], 23, 59, 59)
        # print(begin_date, end_date)
        st = datetime.datetime.now()
        result_json = dict()
        rs_list = []
        try:
            qs = StatisticsMonthlyReason.objects.filter(yearNum=year, monthNum=month)
            if qs:
                for profession in ['其他', '配置', '设备', '线路', '动环及配套']:
                    d = dict(profession=profession)
                    for q in qs:
                        if q.reason == profession:
                            d.update({q.district: str(q.amount)})
                    rs_list.append(d)
            else:
                rs_list = get_district_malfunction_reason(begin_date, end_date)
                for rs in rs_list:
                    for district in ['PRD_1', 'PRD_2', 'GD_N', 'GD_E', 'GD_W']:
                        StatisticsMonthlyReason(yearNum=year, monthNum=month,
                                                district=district, reason=rs['profession'],
                                                amount=rs.get(district, 0)).save()
            result_json['result'] = rs_list
            result_json['process_time'] = str(datetime.datetime.now() - st)
            result_json['status'] = 'success'
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FileUploadParser,)

    def post(self, request, filename):
        # def post(self, request):

        st = datetime.datetime.now()
        result_json = dict()
        try:
            # 使用binary方式上传文件
            file = request.FILES.get('file')
            if filename == 'mf_data':
                parse_malfunction_data_xlsx(file)
                result_json['msg'] = '故障数据上传完成'
            if filename == 'longtime_data':
                parse_malfunction_longtime(file.read())
                result_json['msg'] = '超72小时工单文件上传完成'
            if filename == 'track_data':
                parse_malfunction_track(file.read())
                result_json['msg'] = '遗留跟踪单文件上传完成'
            # print(len(file))
            # print(filename)
            # print(file.name)
            # rs_list = parse_indicators_xls(file.read())

            result_json['process_time'] = str(datetime.datetime.now() - st)
            result_json['status'] = 'success'
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


# 指标文件.xls上传
class IndicatorUploadView(APIView):
    # parser_classes = (MultiPartParser, FileUploadParser,)

    def post(self, request, year, num):
        # def post(self, request):

        st = datetime.datetime.now()
        result_json = dict()
        try:
            files = request.FILES.getlist('rate_data')
            if request.POST.get('type', '') == 'month':
                parse_indicators_xls(files[0].read(), type='month', year=year, month=num)
            elif request.POST.get('type', '') == 'quarter':
                parse_indicators_xls(files[0].read(), type='quarter', year=year, quarter=num)
            result_json['msg'] = '指标文件上传完成'
            result_json['process_time'] = str(datetime.datetime.now() - st)
            result_json['status'] = 'success'
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


class Worst10DepartmentView(APIView):

    def get(self, request, year, month):
        begin_date = datetime.date(year, month, 1)
        end_date = datetime.datetime(year, month, calendar.mdays[month], 23, 59, 59)
        # print(begin_date, end_date)
        st = datetime.datetime.now()
        result_json = dict()
        rs_list = []
        try:
            qs = StatisticsMonthlyWorst10Department.objects.filter(yearNum=year, monthNum=month)
            if qs:
                for q in qs:
                    d = dict(department=q.department,
                             total_amount=str(q.totalAmount),
                             intime_amount=str(q.intimeAmount),
                             timeout_admount=str(q.overtimeAmount),
                             intime_rate=str(q.intimeRate))
                    rs_list.append(d)
            else:
                rs_list = get_worst10_department(begin_date, end_date)
                for rs in rs_list:
                    StatisticsMonthlyWorst10Department(yearNum=year, monthNum=month,
                                                       department=rs['department'],
                                                       totalAmount=rs['total_amount'],
                                                       intimeAmount=rs['intime_amount'],
                                                       overtimeAmount=rs['timeout_admount'],
                                                       intimeRate=rs['intime_rate']
                                                       ).save()
            result_json['result'] = rs_list
            result_json['process_time'] = str(datetime.datetime.now() - st)
            result_json['status'] = 'success'
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


class CityRateView(APIView):

    def get(self, request, year, month):
        st = datetime.datetime.now()
        result_json = dict()
        try:
            rs_list = []
            sorted_list = []
            qs = StatisticsMonthlyQuality.objects.filter(yearNum=year, monthNum=int(month))
            cities = City.objects.all()
            for q in qs:
                d = dict()
                d['city'] = q.city
                d['signRate'] = str(q.signRate)
                d['autoRate'] = str(q.autoRate)
                d['dealRate'] = str(q.dealRate)
                rs_list.append(d)
            for city_obj in cities:
                for d in rs_list:
                    if city_obj.city == d['city']:
                        sorted_list.append(d)
            result_json['result'] = sorted_list
            result_json['process_time'] = str(datetime.datetime.now() - st)
            result_json['status'] = 'success'
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


class WeeklyLongTimeView(APIView):

    def get(self, request):
        st = datetime.datetime.now()
        result_json = dict()
        try:
            rs_list = collect_longtime_weekly()
            result_json['result'] = rs_list
            result_json['process_time'] = str(datetime.datetime.now() - st)
            result_json['status'] = 'success'
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


class WeeklyTrackView(APIView):
    def get(self, request, begin_date, end_date):
        st = datetime.datetime.now()
        result_json = dict()
        try:
            rs_list = collect_track_weekly(begin_date, end_date)
            result_json['result'] = rs_list
            result_json['process_time'] = str(datetime.datetime.now() - st)
            result_json['status'] = 'success'
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


class Top10NeExportView(APIView):

    def get(self, request, year, month):
        filepath, filename = export_top10ne(year, month)

        response = FileResponse(open(filepath, 'rb'))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(filename))

        return response


class DocxExportView(APIView):

    def get(self, request, type, arg1, arg2):
        print(type, arg1, arg2)
        if type == 'month':
            filepath, filename = monthly_export_docx(int(arg1), int(arg2))
        if type == 'quarter':
            filepath, filename = quarterly_export_docx(arg1, arg2)
        if type == 'week':
            filepath, filename = weekly_export_docx(arg1, arg2)

        response = FileResponse(open(filepath, 'rb'))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(filename))

        return response


class Base64ImageView(APIView):
    def post(self, request):
        type = request.POST.get('type', '')
        if type == 'month':
            year = request.POST.get('yearNum', '')
            month = int(request.POST.get('monthNum', ''))
            monthly_amount = request.POST.get('monthly_amount', '')
            monthly_reason = request.POST.get('monthly_reason', '')
            monthly_quality = request.POST.get('monthly_quality', '')
            if monthly_amount:
                save_base64(monthly_amount, 'monthly_amount_' + str(year) + '_' + str(month) + '.png')
            if monthly_reason:
                save_base64(monthly_reason, 'monthly_reason_' + str(year) + '_' + str(month) + '.png')
            if monthly_quality:
                save_base64(monthly_quality, 'monthly_quality_' + str(year) + '_' + str(month) + '.png')
        if type == 'quarter':
            beginDate = request.POST.get('beginDate', '')
            endDate = request.POST.get('endDate', '')
            quarterly_amount = request.POST.get('quarterly_amount', '')
            quarterly_intime = request.POST.get('quarterly_intime', '')
            quarterly_dealtime = request.POST.get('quarterly_dealtime', '')
            quarterly_over48 = request.POST.get('quarterly_over48', '')
            quarterly_reason_amount = request.POST.get('quarterly_reason_amount', '')
            quarterly_specific_amount = request.POST.get('quarterly_specific_amount', '')
            quarterly_specific_dealtime = request.POST.get('quarterly_specific_dealtime', '')
            if quarterly_amount:
                save_base64(quarterly_amount, 'quarterly_amount_' + beginDate + '_' + endDate + '.png')
            if quarterly_intime:
                save_base64(quarterly_intime, 'quarterly_intime_' + beginDate + '_' + endDate + '.png')
            if quarterly_dealtime:
                save_base64(quarterly_dealtime, 'quarterly_dealtime_' + beginDate + '_' + endDate + '.png')
            if quarterly_over48:
                save_base64(quarterly_over48, 'quarterly_over48_' + beginDate + '_' + endDate + '.png')
            if quarterly_reason_amount:
                save_base64(quarterly_reason_amount, 'quarterly_reason_amount_' + beginDate + '_' + endDate + '.png')
            if quarterly_specific_amount:
                save_base64(quarterly_specific_amount, 'quarterly_specific_amount_' + beginDate + '_' + endDate + '.png')
            if quarterly_specific_dealtime:
                save_base64(quarterly_specific_dealtime, 'quarterly_specific_dealtime_' + beginDate + '_' + endDate + '.png')
        if type == 'week':
            beginDate = request.POST.get('beginDate', '')
            endDate = request.POST.get('endDate', '')
            weekly_track = request.POST.get('weekly_track', '')
            weekly_longtime = request.POST.get('weekly_longtime', '')
            if weekly_track:
                save_base64(weekly_track, 'weekly_track_' + beginDate + '_' + endDate + '.png')
            if weekly_longtime:
                save_base64(weekly_longtime, 'weekly_longtime_' + beginDate + '_' + endDate + '.png')
        return JsonResponse(data={'msg': 'OK'})
