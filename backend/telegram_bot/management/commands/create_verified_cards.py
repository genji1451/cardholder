"""
Management команда для массового создания верифицированных карт
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from apps.cards.models import Card
from telegram_bot.models import VerifiedCard
from telegram_bot.utils import create_card_qr_code, get_qr_codes_directory
import os


class Command(BaseCommand):
    help = 'Создаёт верифицированные карты для всех карт в базе данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--series',
            type=int,
            help='Создать только для указанной серии',
        )
        parser.add_argument(
            '--generate-qr',
            action='store_true',
            help='Генерировать QR-коды и сохранять их в файлы',
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Перезаписать существующие верификации',
        )

    def handle(self, *args, **options):
        series_filter = options.get('series')
        generate_qr = options.get('generate_qr', False)
        overwrite = options.get('overwrite', False)

        # Получаем карты
        cards = Card.objects.all()
        if series_filter:
            cards = cards.filter(series__number=series_filter)
            self.stdout.write(f'📚 Обработка карт серии {series_filter}')
        else:
            self.stdout.write('📚 Обработка всех карт')

        created_count = 0
        skipped_count = 0
        qr_generated = 0

        bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'your_bot')
        qr_dir = get_qr_codes_directory() if generate_qr else None

        for card in cards:
            # Проверяем, существует ли уже верификация
            existing = VerifiedCard.objects.filter(card=card).first()
            
            if existing and not overwrite:
                self.stdout.write(
                    self.style.WARNING(f'⏭️  Пропускаем {card.title} #{card.number} (уже существует)')
                )
                skipped_count += 1
                continue
            
            if existing and overwrite:
                existing.delete()
                self.stdout.write(
                    self.style.WARNING(f'🔄 Перезаписываем {card.title} #{card.number}')
                )

            # Создаём верифицированную карту
            verified_card = VerifiedCard.objects.create(
                card=card,
                notes=f'Автоматически создано для {card.series.title}'
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Создана верификация для {card.title} #{card.number}')
            )
            created_count += 1

            # Генерируем QR-код если нужно
            if generate_qr and qr_dir:
                qr_filename = f'card_{card.series.number}_{card.number}.png'
                qr_path = os.path.join(qr_dir, qr_filename)
                
                create_card_qr_code(verified_card, bot_username, save_path=qr_path)
                self.stdout.write(f'   📱 QR-код сохранён: {qr_filename}')
                qr_generated += 1

        # Итоги
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'✅ Создано верификаций: {created_count}'))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'⏭️  Пропущено: {skipped_count}'))
        if qr_generated > 0:
            self.stdout.write(self.style.SUCCESS(f'📱 QR-кодов сгенерировано: {qr_generated}'))
            self.stdout.write(f'   Папка: {qr_dir}')
        self.stdout.write('='*50)

