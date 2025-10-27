"""
URL конфигурация для Telegram Bot API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from telegram_bot.views import VerifiedCardViewSet, VerificationLogViewSet

router = DefaultRouter()
router.register(r'verified-cards', VerifiedCardViewSet, basename='verified-card')
router.register(r'verification-logs', VerificationLogViewSet, basename='verification-log')

app_name = 'telegram_bot'

urlpatterns = [
    path('', include(router.urls)),
]

