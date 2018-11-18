from django.urls import path, re_path

from report.statistics_views import OrderAmountView, IntimeRateView, DealtimeView, Over48RateView, DealQualityView, SpecificDealtimeAmountView, \
    Top10NeView, SumAmountComparedView, DistrictReasonView, FileUploadView, Worst10DepartmentView, CityRateView, Top10NeExportView, \
    WeeklyLongTimeView, WeeklyTrackView, IndicatorUploadView

from django.views.decorators.cache import cache_page

app_name = "report"
urlpatterns = [
    path('amount/<str:begin_date>/<str:end_date>/', cache_page(60 * 60 * 24)(OrderAmountView.as_view())),
    path('intimerate/<str:begin_date>/<str:end_date>/', cache_page(60 * 60 * 24)(IntimeRateView.as_view())),
    path('dealtime/<str:begin_date>/<str:end_date>/', cache_page(60 * 60 * 24)(DealtimeView.as_view())),
    path('over48rate/<str:begin_date>/<str:end_date>/', cache_page(60 * 60 * 24)(Over48RateView.as_view())),
    path('quality/<str:begin_date>/<str:end_date>/', cache_page(60 * 60 * 24)(DealQualityView.as_view())),
    path('specific/<str:begin_date>/<str:end_date>/', cache_page(60 * 60 * 24)(SpecificDealtimeAmountView.as_view())),
    path('top10ne/<int:year>/<int:month>', Top10NeView.as_view()),
    path('amountcompare/<int:year>/<int:month>', cache_page(60 * 60 * 24)(SumAmountComparedView.as_view())),
    path('districtreason/<int:year>/<int:month>', cache_page(60 * 60 * 24)(DistrictReasonView.as_view())),
    path('cityrate/<year>/<month>', CityRateView.as_view()),
    # path('upload/', FileUploadView.as_view()),
    # 直接上传binary方式
    path('upload/<filename>', FileUploadView.as_view()),
    # 指标文件上传
    path('indicator/<year>/<num>', IndicatorUploadView.as_view()),
    path('worst10department/<int:year>/<int:month>', cache_page(60 * 60 * 24)(Worst10DepartmentView.as_view())),
    path('longtime/', WeeklyLongTimeView.as_view()),
    path('track/<str:begin_date>/<str:end_date>/', WeeklyTrackView.as_view()),
    path('top10ne/export/<int:year>/<int:month>', Top10NeExportView.as_view())

]
