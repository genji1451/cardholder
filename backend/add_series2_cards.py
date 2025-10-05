#!/usr/bin/env python3
"""
Скрипт для добавления карточек второй серии Spider-Man (276-550)
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

def add_series2_cards():
    """Добавляем карточки второй серии Spider-Man (276-550)"""
    print("🕷️ Добавляем карточки второй серии Spider-Man (276-550)...")
    
    # Получаем или создаем вторую серию
    series, created = Series.objects.get_or_create(
        number=2,
        defaults={'title': 'Spider-Man Heroes and Villains - Part 2'}
    )
    
    if created:
        print(f"✅ Создана серия: {series.title}")
    else:
        print(f"✅ Используем существующую серию: {series.title}")
    
    # Данные карточек второй серии (276-550)
    cards_data = {
        # Герои и персонажи (276-350)
        276: {"title": "Человек-Паук (Классический)", "type": "Герой", "rarity": "o", "price": 52.50},
        277: {"title": "Железный Человек (Марк 42)", "type": "Герой", "rarity": "o", "price": 55.00},
        278: {"title": "Капитан Америка (Стив Роджерс)", "type": "Герой", "rarity": "o", "price": 57.50},
        279: {"title": "Тор (Одинсон)", "type": "Герой", "rarity": "o", "price": 60.00},
        280: {"title": "Халк (Брюс Баннер)", "type": "Герой", "rarity": "o", "price": 62.50},
        281: {"title": "Черная Вдова (Наташа Романофф)", "type": "Герой", "rarity": "o", "price": 65.00},
        282: {"title": "Соколиный Глаз (Клинт Бартон)", "type": "Герой", "rarity": "o", "price": 67.50},
        283: {"title": "Доктор Стрэндж (Стивен Стрэндж)", "type": "Герой", "rarity": "o", "price": 70.00},
        284: {"title": "Сорвиголова (Мэтт Мердок)", "type": "Герой", "rarity": "o", "price": 72.50},
        285: {"title": "Джессика Джонс (Джессика Кэмпбелл)", "type": "Герой", "rarity": "o", "price": 75.00},
        286: {"title": "Люк Кейдж (Карл Лукас)", "type": "Герой", "rarity": "o", "price": 77.50},
        287: {"title": "Железный Кулак (Дэнни Рэнд)", "type": "Герой", "rarity": "o", "price": 80.00},
        288: {"title": "Человек-Паук (Майлз Моралес)", "type": "Герой", "rarity": "ск", "price": 85.00},
        289: {"title": "Человек-Паук (Гвен Стейси)", "type": "Герой", "rarity": "ск", "price": 87.50},
        290: {"title": "Человек-Паук (Бен Рейли)", "type": "Герой", "rarity": "ск", "price": 90.00},
        291: {"title": "Веном (Эдди Брок)", "type": "Антигерой", "rarity": "ск", "price": 92.50},
        292: {"title": "Карнаж (Клетус Кассади)", "type": "Злодей", "rarity": "ск", "price": 95.00},
        293: {"title": "Токсин (Патрик Маллиган)", "type": "Антигерой", "rarity": "ск", "price": 97.50},
        294: {"title": "Анти-Веном (Эдди Брок)", "type": "Антигерой", "rarity": "ск", "price": 100.00},
        295: {"title": "Серебряный Сёрфер (Норрин Радд)", "type": "Герой", "rarity": "ск", "price": 102.50},
        296: {"title": "Фантастическая Четверка (Рид Ричардс)", "type": "Герой", "rarity": "ск", "price": 105.00},
        297: {"title": "Мистер Фантастик (Рид Ричардс)", "type": "Герой", "rarity": "ск", "price": 107.50},
        298: {"title": "Невидимая Женщина (Сьюзан Шторм)", "type": "Герой", "rarity": "ск", "price": 110.00},
        299: {"title": "Человек-Факел (Джонни Шторм)", "type": "Герой", "rarity": "ск", "price": 112.50},
        300: {"title": "Существо (Бен Гримм)", "type": "Герой", "rarity": "ск", "price": 115.00},
    }
    
    # Добавляем больше карточек (301-400)
    for i in range(301, 401):
        card_type = "Герой" if i <= 350 else "Злодей" if i <= 380 else "Антигерой"
        rarity = "o" if i <= 320 else "ск" if i <= 370 else "ук"
        price = 60.00 + (i * 2.50)
        
        cards_data[i] = {
            "title": f"Карточка #{i}",
            "type": card_type,
            "rarity": rarity,
            "price": price
        }
    
    # Добавляем карточки (401-550)
    for i in range(401, 551):
        card_type = "Боевая карточка" if i <= 450 else "Суперместа" if i <= 500 else "Классическая обложка"
        rarity = "ск" if i <= 450 else "ук" if i <= 500 else "ук"
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
            card.notes = f"{data['type']}: {data['title']}\nИзображение: https://www.laststicker.ru/i/cards/106/{card_number}.jpg"
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
                notes=f"{data['type']}: {data['title']}\nИзображение: https://www.laststicker.ru/i/cards/106/{card_number}.jpg"
            )
            created_count += 1
        
        if (created_count + updated_count) % 50 == 0:
            print(f"✅ Обработано {created_count + updated_count} карточек...")
    
    print(f"✅ Создано карточек: {created_count}")
    print(f"✅ Обновлено карточек: {updated_count}")
    print(f"📊 Всего обработано: {created_count + updated_count}")
    
    return created_count + updated_count

def add_series2_to_inventory():
    """Добавляем карточки второй серии в инвентарь"""
    print("🕷️ Добавляем карточки второй серии в инвентарь...")
    
    # Получаем пользователя
    user = User.objects.get(username='spiderman_collector')
    
    # Получаем вторую серию
    series = Series.objects.get(number=2)
    
    # Получаем все карточки второй серии
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
    print("🕷️ Добавление карточек второй серии Spider-Man (276-550)")
    
    # Добавляем карточки
    cards_count = add_series2_cards()
    
    # Добавляем в инвентарь
    inventory_count = add_series2_to_inventory()
    
    print(f"\n🎉 Добавление завершено!")
    print(f"📊 Карточек добавлено: {cards_count}")
    print(f"📊 Элементов в инвентаре: {inventory_count}")
    print(f"🌐 Изображения: https://www.laststicker.ru/i/cards/106/[номер].jpg")

if __name__ == '__main__':
    main()
