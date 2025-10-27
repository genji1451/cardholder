"""
Management команда для запуска обновлённого Telegram бота с админкой
"""

from django.core.management.base import BaseCommand
from telegram_bot.bot_new import main


class Command(BaseCommand):
    help = 'Запускает обновлённый Telegram бота с админ-панелью'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🤖 Запуск обновлённого Telegram бота...'))
        self.stdout.write(self.style.SUCCESS('✨ Новые возможности:'))
        self.stdout.write('   - Админ-панель в боте')
        self.stdout.write('   - Загрузка фотографий карт')
        self.stdout.write('   - Генерация QR-кодов через бота')
        self.stdout.write('   - Отображение 2 фото клиентам')
        self.stdout.write(self.style.WARNING('\nДля остановки нажмите Ctrl+C\n'))
        
        try:
            main()
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('\n✅ Бот остановлен'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка: {e}'))

