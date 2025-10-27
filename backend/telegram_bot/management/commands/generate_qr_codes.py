"""
Management команда для генерации QR-кодов
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from telegram_bot.models import VerifiedCard
from telegram_bot.utils import create_card_qr_code, generate_printable_card_label, get_qr_codes_directory
import os


class Command(BaseCommand):
    help = 'Генерирует QR-коды для верифицированных карт'

    def add_arguments(self, parser):
        parser.add_argument(
            '--card-id',
            type=int,
            help='Сгенерировать только для указанной карты',
        )
        parser.add_argument(
            '--with-labels',
            action='store_true',
            help='Генерировать также метки для печати',
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            help='Директория для сохранения (по умолчанию MEDIA_ROOT/qr_codes)',
        )

    def handle(self, *args, **options):
        card_id = options.get('card_id')
        with_labels = options.get('with_labels', False)
        output_dir = options.get('output_dir') or get_qr_codes_directory()

        # Создаём директории
        os.makedirs(output_dir, exist_ok=True)
        if with_labels:
            labels_dir = os.path.join(output_dir, 'labels')
            os.makedirs(labels_dir, exist_ok=True)

        # Получаем верифицированные карты
        verified_cards = VerifiedCard.objects.select_related('card', 'card__series').all()
        if card_id:
            verified_cards = verified_cards.filter(card_id=card_id)

        if not verified_cards.exists():
            self.stdout.write(self.style.ERROR('❌ Верифицированные карты не найдены'))
            return

        bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'your_bot')
        
        generated_count = 0
        labels_count = 0

        self.stdout.write(f'📱 Генерация QR-кодов для {verified_cards.count()} карт...')
        self.stdout.write(f'📁 Папка: {output_dir}\n')

        for verified_card in verified_cards:
            card = verified_card.card
            
            # Генерируем QR-код
            qr_filename = f'card_{card.series.number}_{card.number}_qr.png'
            qr_path = os.path.join(output_dir, qr_filename)
            
            try:
                create_card_qr_code(verified_card, bot_username, save_path=qr_path)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ {card.title} #{card.number} → {qr_filename}'
                    )
                )
                generated_count += 1

                # Генерируем метку если нужно
                if with_labels:
                    label_filename = f'card_{card.series.number}_{card.number}_label.png'
                    label_path = os.path.join(labels_dir, label_filename)
                    
                    label_buffer = generate_printable_card_label(verified_card, bot_username)
                    with open(label_path, 'wb') as f:
                        f.write(label_buffer.getvalue())
                    
                    self.stdout.write(f'   🏷️  Метка сохранена: {label_filename}')
                    labels_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Ошибка для {card.title} #{card.number}: {e}'
                    )
                )

        # Итоги
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'✅ QR-кодов сгенерировано: {generated_count}'))
        if labels_count > 0:
            self.stdout.write(self.style.SUCCESS(f'🏷️  Меток сгенерировано: {labels_count}'))
        self.stdout.write(f'📁 Результаты сохранены в: {output_dir}')
        self.stdout.write('='*50)

