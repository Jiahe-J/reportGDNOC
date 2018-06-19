"""DataEcharts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from report import frontend_views, backend_views

urlpatterns = [
    path('', frontend_views.IndexView.as_view(), name='index'),
    path('frontend_charts_list/', frontend_views.FrontendEchartsTemplate.as_view(), name='frontend_demo'),
    path('backend_charts_list/', backend_views.BackendEChartsTemplate.as_view(), name='backend_demo'),

    path('multiple/Page/', backend_views.PageDemoView.as_view(), name='page_demo'),
    path('multiple/NamedCharts/', backend_views.NamedChartsView.as_view(), name='namedcharts_demo'),
    path('demo/temperature/', backend_views.TemperatureEChartsView.as_view()),
    path('options/reportDemo/', frontend_views.ReportDemoEchartsTemplate.as_view(), name='report_demo'),

    # Options Json for frontend views
    path('options/simpleBar/', frontend_views.SimpleBarView.as_view()),
    path('options/simpleKLine/', frontend_views.SimpleKLineView.as_view()),
    path('options/simpleMap/', frontend_views.SimpleMapView.as_view()),
    path('options/simplePie/', frontend_views.SimplePieView.as_view()),
    path('options/wordCloud/', frontend_views.WordCloudView.as_view()),
    path('options/reportBar/', frontend_views.ReportDemoView.as_view()),
    path('upload_file/', frontend_views.TestView.as_view())

]
