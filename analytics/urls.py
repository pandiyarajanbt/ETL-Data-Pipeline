from django.urls import path
from .views import PipelineSummaryView, TableStatsView

urlpatterns = [
    path('summary/', PipelineSummaryView.as_view()),
    path('table-stats/', TableStatsView.as_view()),
]
