# coding=utf8
from django.http import JsonResponse
from django.views.generic.base import View

from utils.data_collect import collect_order_amount_chart, collect_order_amount_table, collect_deal_time, collect_over_48h_rate, \
    collect_deal_in_time_rate


class OrderAmountView(View):
    def post(self, request):
        year = request.POST.get('year', '')
        quarter = request.POST.get('quarter', '')
        target = request.POST.get('target')
        result_json = dict()
        if target == 'table':
            result_json = collect_order_amount_table(int(year), int(quarter))
            return JsonResponse(data=result_json, safe=False)
        if target == 'chart':
            result_json = collect_order_amount_chart(int(year), int(quarter))

        else:
            result_json['msg'] = "请求参数有误"
            result_json['status'] = "fail"
        return JsonResponse(data=result_json, safe=False)


class IntimeRateView(View):
    def post(self, request):
        result_json = dict()
        try:
            year = request.POST.get('year', '')
            quarter = request.POST.get('quarter', '')
            result_json = collect_deal_in_time_rate(int(year), int(quarter))
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


class DealtimeView(View):
    def post(self, request):
        result_json = dict()
        try:
            year = request.POST.get('year', '')
            quarter = request.POST.get('quarter', '')
            result_json = collect_deal_time(int(year), int(quarter))
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)


class Over48Rate(View):
    def post(self, request):
        result_json = dict()
        try:
            year = request.POST.get('year', '')
            quarter = request.POST.get('quarter', '')
            result_json = collect_over_48h_rate(int(year), int(quarter))
            return JsonResponse(data=result_json, safe=False)
        except Exception as e:
            result_json['status'] = 'fail'
            result_json['msg'] = str(e)
            return JsonResponse(data=result_json, safe=False)
