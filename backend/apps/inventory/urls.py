from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'items', views.InventoryItemViewSet)
router.register(r'images', views.CardImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
