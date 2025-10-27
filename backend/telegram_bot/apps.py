"""
Конфигурация приложения Telegram Bot
"""

from django.apps import AppConfig


class TelegramBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_bot'
    verbose_name = 'Telegram Bot'
    
    def ready(self):
        """Инициализация приложения"""
        pass

