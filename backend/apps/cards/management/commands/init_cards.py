#!/usr/bin/env python3
"""
Django команда для инициализации карточек Spider-Man
"""

from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.cards.models import Card, Series


class Command(BaseCommand):
    help = 'Инициализирует карточки Spider-Man'

    def handle(self, *args, **options):
        self.stdout.write('🕷️ Инициализируем карточки Spider-Man...')
        
        # Создаем серию если не существует
        series, created = Series.objects.get_or_create(
            number=1,
            defaults={
                'title': 'Spider-Man Collection',
                'description': 'Основная коллекция карточек Человека-Паука'
            }
        )
        
        if created:
            self.stdout.write(f'✅ Создана серия: {series.title}')
        else:
            self.stdout.write(f'📋 Серия уже существует: {series.title}')
        
        # Создаем несколько основных карточек для тестирования
        test_cards = [
            {
                'number': 1,
                'title': 'Человек-Паук',
                'type': 'Герой',
                'rarity': 'o',
                'base_price_rub': Decimal('52.50'),
                'description': 'Основной герой комиксов Marvel'
            },
            {
                'number': 2,
                'title': 'Железный Человек',
                'type': 'Герой',
                'rarity': 'o',
                'base_price_rub': Decimal('55.00'),
                'description': 'Гений, миллиардер, филантроп'
            },
            {
                'number': 3,
                'title': 'Капитан Америка',
                'type': 'Герой',
                'rarity': 'o',
                'base_price_rub': Decimal('57.50'),
                'description': 'Символ свободы и справедливости'
            },
            {
                'number': 4,
                'title': 'Веном',
                'type': 'Антигерой',
                'rarity': 'ск',
                'base_price_rub': Decimal('92.50'),
                'description': 'Симбиот и бывший хост Эдди Брок'
            },
            {
                'number': 5,
                'title': 'Зеленый Гоблин',
                'type': 'Злодей',
                'rarity': 'р',
                'base_price_rub': Decimal('85.00'),
                'description': 'Главный враг Человека-Паука'
            }
        ]
        
        created_count = 0
        for card_data in test_cards:
            card, created = Card.objects.get_or_create(
                number=card_data['number'],
                series=series,
                defaults=card_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'✅ Создана карточка: {card.title}')
            else:
                self.stdout.write(f'📋 Карточка уже существует: {card.title}')
        
        total_cards = Card.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 Инициализация завершена! Создано карточек: {created_count}, '
                f'всего в базе: {total_cards}'
            )
        )
