"""
Management команда для проверки и завершения брейков

Использование:
    python manage.py check_breaks

Эта команда должна запускаться периодически (например, через cron каждую минуту)
"""

from django.core.management.base import BaseCommand
from telegram_bot.tasks import check_and_complete_breaks


class Command(BaseCommand):
    help = 'Проверяет и завершает брейки, у которых истёк срок'

    def handle(self, *args, **options):
        self.stdout.write('Проверка брейков...')
        
        try:
            check_and_complete_breaks()
            self.stdout.write(self.style.SUCCESS('✅ Проверка завершена успешно'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка: {e}'))
            raise
