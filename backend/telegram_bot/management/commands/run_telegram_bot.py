"""
Management команда для запуска Telegram бота
"""

from django.core.management.base import BaseCommand
from telegram_bot.bot import main


class Command(BaseCommand):
    help = 'Запускает Telegram бота для проверки подлинности карт'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🤖 Запуск Telegram бота...'))
        self.stdout.write(self.style.WARNING('Для остановки нажмите Ctrl+C'))
        
        try:
            main()
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('\n✅ Бот остановлен'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка: {e}'))

