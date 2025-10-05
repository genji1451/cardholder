from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'trades', views.TradeViewSet)
router.register(r'prices', views.PriceRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
