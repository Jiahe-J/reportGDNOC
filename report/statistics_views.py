# coding=utf8
from datetime import datetime

from django.http import JsonResponse
from django.views.generic.base import View

from utils.data_collect import collect_order_amount_chart, collect_order_amount_table, collect_deal_time, collect_over_48h_rate, \
    collect_deal_in_time_rate, collect_deal_quality, collect_specific_dealtime_amount
from utils.top10_Ne import get_top10_ne


def get_parameter(request):
    statistics_type = int(request.POST.get("statisticsType", 0))
    year = int(request.POST.get('year', 1))
    quarter = int(request.POST.get('quarter', 1))
    month = int(request.POST.get('month', 1))
    day = int(request.POST.get('day', 1))
    begin_datetime = str(request.POST.get('begin_datetime', ""))
    end_datetime = str(request.POST.get('end_datetime', ""))
    print(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
    return statistics_type, year, quarter, month, day, begin_datetime, end_datetime


class OrderAmountView(View):
    def post(self, request):
        st = datetime.now()
        statistics_type, year, quarter, month, day, begin_datetime, end_datetime = get_parameter(request)
        target = request.POST.get('target', "")
        if target == 'chart':
            result_json = collect_order_amount_chart(statistics_type, year, quarter, month, day)
        else:
            result_json = collect_order_amount_table(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
        result_json['process_time'] = str(datetime.now() - st)
        return JsonResponse(data=result_json, safe=False)


class IntimeRateView(View):
    def post(self, request):
        st = datetime.now()
        result_json = dict()
        try:
            statistics_type, year, quarter, month, day, begin_datetime, end_datetime = get_parameter(request)
            result_json = collect_deal_in_time_rate(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
            result_json['process_time'] = str(datetime.now() - st)
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


class DealtimeView(View):
    def post(self, request):
        st = datetime.now()
        result_json = dict()
        try:
            statistics_type, year, quarter, month, day, begin_datetime, end_datetime = get_parameter(request)
            result_json = collect_deal_time(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
            result_json['process_time'] = str(datetime.now() - st)
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


class Over48RateView(View):
    def post(self, request):
        st = datetime.now()
        result_json = dict()
        try:
            statistics_type, year, quarter, month, day, begin_datetime, end_datetime = get_parameter(request)
            result_json = collect_over_48h_rate(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
            result_json['process_time'] = str(datetime.now() - st)
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


class DealQualityView(View):
    def post(self, request):
        st = datetime.now()
        result_json = dict()
        try:
            statistics_type, year, quarter, month, day, begin_datetime, end_datetime = get_parameter(request)
            result_json = collect_deal_quality(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
            result_json['process_time'] = str(datetime.now() - st)
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


class SpecificDealtimeAmountView(View):
    def post(self, request):
        st = datetime.now()
        result_json = dict()
        try:
            statistics_type, year, quarter, month, day, begin_datetime, end_datetime = get_parameter(request)
            result_json = collect_specific_dealtime_amount(statistics_type, year, quarter, month, day, begin_datetime, end_datetime)
            result_json['process_time'] = str(datetime.now() - st)
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


class Top10NeView(View):
    def post(self, request):
        st = datetime.now()
        result_json = dict()
        try:
            begin_datetime = str(request.POST.get('begin_datetime', ""))
            end_datetime = str(request.POST.get('end_datetime', ""))
            profession_list = ['4G网络', '直放站', 'CDMA网络', '本地传输', '光网络', '动力', '交换接入网', '数据']
            rs_dict = dict()
            for profession in profession_list:
                rs_dict.update(get_top10_ne(begin_datetime, end_datetime, profession))
            result_json['result'] = rs_dict
            result_json['process_time'] = str(datetime.now() - st)
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)