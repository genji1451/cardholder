from django.urls import path
from . import views

urlpatterns = [
    path('overview/', views.AnalyticsOverviewView.as_view(), name='analytics-overview'),
    path('distribution/', views.AnalyticsDistributionView.as_view(), name='analytics-distribution'),
    path('progress/', views.AnalyticsProgressView.as_view(), name='analytics-progress'),
    path('value-trend/', views.AnalyticsValueTrendView.as_view(), name='analytics-value-trend'),
]
