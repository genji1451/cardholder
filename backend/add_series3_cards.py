#!/usr/bin/env python3
"""
Скрипт для добавления карточек третьей серии Spider-Man (551-825)
"""

import os
import sys
import django
from decimal import Decimal

# Настройка Django
sys.path.append('/Users/rex/Documents/cards/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.cards.models import Card, Series
from apps.inventory.models import InventoryItem
from django.contrib.auth.models import User

def add_series3_cards():
    """Добавляем карточки третьей серии Spider-Man (551-825)"""
    print("🕷️ Добавляем карточки третьей серии Spider-Man (551-825)...")
    
    # Получаем или создаем третью серию
    series, created = Series.objects.get_or_create(
        number=3,
        defaults={'title': 'Spider-Man Heroes and Villains - Part 3'}
    )
    
    if created:
        print(f"✅ Создана серия: {series.title}")
    else:
        print(f"✅ Используем существующую серию: {series.title}")
    
    # Данные карточек третьей серии (551-825)
    cards_data = {
        # Герои и персонажи (551-650)
        551: {"title": "Человек-Паук (Классический)", "type": "Герой", "rarity": "o", "price": 52.50},
        552: {"title": "Железный Человек (Марк 85)", "type": "Герой", "rarity": "o", "price": 55.00},
        553: {"title": "Капитан Америка (Стив Роджерс)", "type": "Герой", "rarity": "o", "price": 57.50},
        554: {"title": "Тор (Одинсон)", "type": "Герой", "rarity": "o", "price": 60.00},
        555: {"title": "Халк (Брюс Баннер)", "type": "Герой", "rarity": "o", "price": 62.50},
        556: {"title": "Черная Вдова (Наташа Романофф)", "type": "Герой", "rarity": "o", "price": 65.00},
        557: {"title": "Соколиный Глаз (Клинт Бартон)", "type": "Герой", "rarity": "o", "price": 67.50},
        558: {"title": "Доктор Стрэндж (Стивен Стрэндж)", "type": "Герой", "rarity": "o", "price": 70.00},
        559: {"title": "Сорвиголова (Мэтт Мердок)", "type": "Герой", "rarity": "o", "price": 72.50},
        560: {"title": "Джессика Джонс (Джессика Кэмпбелл)", "type": "Герой", "rarity": "o", "price": 75.00},
        561: {"title": "Люк Кейдж (Карл Лукас)", "type": "Герой", "rarity": "o", "price": 77.50},
        562: {"title": "Железный Кулак (Дэнни Рэнд)", "type": "Герой", "rarity": "o", "price": 80.00},
        563: {"title": "Человек-Паук (Майлз Моралес)", "type": "Герой", "rarity": "ск", "price": 85.00},
        564: {"title": "Человек-Паук (Гвен Стейси)", "type": "Герой", "rarity": "ск", "price": 87.50},
        565: {"title": "Человек-Паук (Бен Рейли)", "type": "Герой", "rarity": "ск", "price": 90.00},
        566: {"title": "Веном (Эдди Брок)", "type": "Антигерой", "rarity": "ск", "price": 92.50},
        567: {"title": "Карнаж (Клетус Кассади)", "type": "Злодей", "rarity": "ск", "price": 95.00},
        568: {"title": "Токсин (Патрик Маллиган)", "type": "Антигерой", "rarity": "ск", "price": 97.50},
        569: {"title": "Анти-Веном (Эдди Брок)", "type": "Антигерой", "rarity": "ск", "price": 100.00},
        570: {"title": "Серебряный Сёрфер (Норрин Радд)", "type": "Герой", "rarity": "ск", "price": 102.50},
    }
    
    # Добавляем больше карточек (571-700)
    for i in range(571, 701):
        card_type = "Герой" if i <= 600 else "Злодей" if i <= 650 else "Антигерой"
        rarity = "o" if i <= 590 else "ск" if i <= 640 else "ук"
        price = 60.00 + (i * 2.50)
        
        cards_data[i] = {
            "title": f"Карточка #{i}",
            "type": card_type,
            "rarity": rarity,
            "price": price
        }
    
    # Добавляем карточки (701-825)
    for i in range(701, 826):
        card_type = "Боевая карточка" if i <= 750 else "Суперместа" if i <= 800 else "Классическая обложка"
        rarity = "ск" if i <= 750 else "ук" if i <= 800 else "ук"
        price = 70.00 + (i * 3.00)
        
        cards_data[i] = {
            "title": f"Карточка #{i}",
            "type": card_type,
            "rarity": rarity,
            "price": price
        }
    
    # Создаем карточки в базе данных
    created_count = 0
    updated_count = 0
    
    for card_number, data in cards_data.items():
        try:
            # Пытаемся найти существующую карточку
            card = Card.objects.get(series=series, number=card_number)
            
            # Обновляем существующую карточку
            card.title = data["title"]
            card.rarity = data["rarity"]
            card.base_price_rub = Decimal(str(data["price"]))
            card.notes = f"{data['type']}: {data['title']}\nИзображение: https://www.laststicker.ru/i/cards/166/{card_number}.jpg"
            card.save()
            updated_count += 1
            
        except Card.DoesNotExist:
            # Создаем новую карточку
            card = Card.objects.create(
                series=series,
                number=card_number,
                title=data["title"],
                rarity=data["rarity"],
                base_price_rub=Decimal(str(data["price"])),
                notes=f"{data['type']}: {data['title']}\nИзображение: https://www.laststicker.ru/i/cards/166/{card_number}.jpg"
            )
            created_count += 1
        
        if (created_count + updated_count) % 50 == 0:
            print(f"✅ Обработано {created_count + updated_count} карточек...")
    
    print(f"✅ Создано карточек: {created_count}")
    print(f"✅ Обновлено карточек: {updated_count}")
    print(f"📊 Всего обработано: {created_count + updated_count}")
    
    return created_count + updated_count

def add_series3_to_inventory():
    """Добавляем карточки третьей серии в инвентарь"""
    print("🕷️ Добавляем карточки третьей серии в инвентарь...")
    
    # Получаем пользователя
    user = User.objects.get(username='spiderman_collector')
    
    # Получаем третью серию
    series = Series.objects.get(number=3)
    
    # Получаем все карточки третьей серии
    cards = Card.objects.filter(series=series)
    
    added_count = 0
    
    for card in cards:
        try:
            # Проверяем, есть ли уже такой элемент в инвентаре
            existing_item = InventoryItem.objects.get(owner=user, card=card)
            print(f"ℹ️ Карточка #{card.number} уже есть в инвентаре")
            continue
        except InventoryItem.DoesNotExist:
            pass
        
        # Создаем элемент инвентаря
        InventoryItem.objects.create(
            owner=user,
            card=card,
            quantity=1,
            condition='M',
            user_rating=Decimal('8.5'),
            has_card=True
        )
        
        added_count += 1
        
        if added_count % 50 == 0:
            print(f"✅ Добавлено {added_count} карточек в инвентарь...")
    
    print(f"📊 Добавлено в инвентарь: {added_count} карточек")
    return added_count

def main():
    """Основная функция"""
    print("🕷️ Добавление карточек третьей серии Spider-Man (551-825)")
    
    # Добавляем карточки
    cards_count = add_series3_cards()
    
    # Добавляем в инвентарь
    inventory_count = add_series3_to_inventory()
    
    print(f"\n🎉 Добавление завершено!")
    print(f"📊 Карточек добавлено: {cards_count}")
    print(f"📊 Элементов в инвентаре: {inventory_count}")
    print(f"🌐 Изображения: https://www.laststicker.ru/i/cards/166/[номер].jpg")

if __name__ == '__main__':
    main()
