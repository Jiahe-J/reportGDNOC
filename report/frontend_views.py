# coding=utf8
import os
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView, View
from django_echarts.views.frontend import EChartsFrontView
from pyecharts import Bar
from utils.data_parser import deal_in_time_rate_parser, parse_malfunction_data_xls, parse_malfunction_data_xlsx
from .demo_data import FACTORY


class IndexView(TemplateView):
    template_name = 'index.html'


class FrontendEchartsTemplate(TemplateView):
    template_name = 'frontend_charts.html'


class ReportDemoEchartsTemplate(TemplateView):
    template_name = 'demo.html'


class SimpleBarView(EChartsFrontView):
    def get_echarts_instance(self, **kwargs):
        return FACTORY.create('bar', **kwargs)


# 获取前端参数,处理,返回json
class ReportDemoView(EChartsFrontView):
    def get_echarts_instance(self, **kwargs):
        year = kwargs.get('year')
        quarter = kwargs.get('quarter')
        print(year, quarter)
        print(kwargs.get('year'))
        bar = Bar("故障处理及时率", "珠三角地区")
        cites, rate = deal_in_time_rate_parser()
        bar.add("珠三角地区1", cites, rate)
        bar.renderer = 'svg'
        dt = {'title': [{'text': '故障处理及时率', 'subtext': '珠三角地区', 'left': 'auto', 'top': 'auto', 'textStyle': {'color': '#000', 'fontSize': 18},
                         'subtextStyle': {'color': '#aaa', 'fontSize': 12}}],
              'toolbox': {'show': True, 'orient': 'vertical', 'left': '95%', 'top': 'center',
                          'feature': {'saveAsImage': {'show': True, 'title': '下载图片'}, 'restore': {'show': True}, 'dataView': {'show': True}}},
              'series_id': 2946983, 'tooltip': {'trigger': 'item', 'triggerOn': 'mousemove|click', 'axisPointer': {'type': 'line'}, 'formatter': None,
                                                'textStyle': {'color': '#fff', 'fontSize': 14}, 'backgroundColor': 'rgba(50,50,50,0.7)',
                                                'borderColor': '#333', 'borderWidth': 0}, 'series': [
                {'type': 'bar', 'name': '珠三角地区', 'data': [100, 99, 98, 97, 95, 88, 87, 85], 'stack': '', 'barCategoryGap': '20%',
                 'label': {'normal': {'show': False, 'position': 'top', 'textStyle': {'color': '#000', 'fontSize': 12}, 'formatter': None},
                           'emphasis': {'show': True, 'position': None, 'textStyle': {'color': '#fff', 'fontSize': 12}}}, 'markPoint': {'data': []},
                 'markLine': {'data': []}, 'seriesId': 2946983}], 'legend': [
                {'data': ['珠三角地区'], 'selectedMode': 'multiple', 'show': True, 'left': 'center', 'top': 'top', 'orient': 'horizontal',
                 'textStyle': {'fontSize': 12, 'color': '#333'}}], 'backgroundColor': '#fff', 'xAxis': [
                {'name': '', 'show': True, 'nameLocation': 'middle', 'nameGap': 25, 'nameTextStyle': {'fontSize': 14},
                 'axisLabel': {'interval': 'auto', 'rotate': 0, 'margin': 8, 'textStyle': {'fontSize': 12, 'color': '#000'}},
                 'axisTick': {'alignWithLabel': False}, 'inverse': False, 'position': None, 'boundaryGap': True, 'min': None, 'max': None,
                 'data': ['佛山', '广州', '深圳', '东莞', '中山', '珠海', '惠州', '江门'], 'type': 'category'}], 'yAxis': [
                {'name': '', 'show': True, 'nameLocation': 'middle', 'nameGap': 25, 'nameTextStyle': {'fontSize': 14},
                 'axisLabel': {'formatter': '{value} ', 'rotate': 0, 'interval': 'auto', 'margin': 8, 'textStyle': {'fontSize': 12, 'color': '#000'}},
                 'axisTick': {'alignWithLabel': False}, 'inverse': False, 'position': None, 'boundaryGap': True, 'min': None, 'max': None,
                 'splitLine': {'show': True}, 'type': 'value'}],
              'color': ['#c23531', '#2f4554', '#61a0a8', '#d48265', '#749f83', '#ca8622', '#bda29a', '#6e7074', '#546570', '#c4ccd3', '#f05b72',
                        '#ef5b9c', '#f47920', '#905a3d', '#fab27b', '#2a5caa', '#444693', '#726930', '#b2d235', '#6d8346', '#ac6767', '#1d953f',
                        '#6950a1', '#918597', '#f6f5ec']}

        return dt  # 相当于bar.options

    def get(self, request, **kwargs):
        year = request.GET.get('year', '')
        quarter = request.GET.get('quarter', '')
        kwargs.__setitem__('year', year)
        kwargs.__setitem__('quarter', quarter)
        echarts_instance = self.get_echarts_instance(**kwargs)
        # print(year, quarter)
        # print(kwargs.get('year'))
        print(echarts_instance)
        return JsonResponse(data=echarts_instance, safe=False)


class SimpleKLineView(EChartsFrontView):
    def get_echarts_instance(self, **kwargs):
        return FACTORY.create('kline')


class SimpleMapView(EChartsFrontView):
    def get_echarts_instance(self, **kwargs):
        return FACTORY.create('map')


class SimplePieView(EChartsFrontView):
    def get_echarts_instance(self, **kwargs):
        return FACTORY.create('pie')


class WordCloudView(EChartsFrontView):
    def get_echarts_instance(self, *args, **kwargs):
        return FACTORY.create('word_cloud')


# 测试:从前端获取文件,解析入库
class TestView(View):
    def post(self, request):
        file_contents = request.FILES.getlist('excel')
        for f in file_contents:
            if os.path.splitext(f.name)[1] == '.xlsx':
                parse_malfunction_data_xlsx(filename=f)
            else:
                parse_malfunction_data_xls(file_contents=f.read())
        return render(request, 'demo.html')
