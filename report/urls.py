from django.urls import path, re_path

from report.statistics_views import OrderAmountView, IntimeRateView, DealtimeView, Over48RateView, DealQualityView, ReasonAmountView

app_name = "report"
urlpatterns = [
    path('amount/', OrderAmountView.as_view()),
    path('intimerate/', IntimeRateView.as_view()),
    path('dealtime/', DealtimeView.as_view()),
    path('over48rate/', Over48RateView.as_view()),
    path('quality/', DealQualityView.as_view()),
    path('reason/', ReasonAmountView.as_view())
]
