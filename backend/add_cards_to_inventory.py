#!/usr/bin/env python3
"""
Скрипт для добавления всех карточек Spider-Man в инвентарь пользователя
"""

import os
import sys
import django
from decimal import Decimal
import random

# Настройка Django
sys.path.append('/Users/rex/Documents/cards/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.cards.models import Card, Series
from apps.inventory.models import InventoryItem
from django.contrib.auth.models import User

def add_cards_to_inventory():
    """Добавляем все карточки в инвентарь пользователя"""
    print("🕷️ Добавляем все карточки Spider-Man в инвентарь...")
    
    # Получаем или создаем пользователя
    user, created = User.objects.get_or_create(
        username='spiderman_collector',
        defaults={
            'email': 'collector@spiderman.com',
            'first_name': 'Spider-Man',
            'last_name': 'Collector'
        }
    )
    
    if created:
        print(f"✅ Создан пользователь: {user.username}")
    else:
        print(f"✅ Используем существующего пользователя: {user.username}")
    
    # Получаем все карточки
    all_cards = Card.objects.all()
    print(f"📊 Найдено карточек: {all_cards.count()}")
    
    added_count = 0
    updated_count = 0
    
    for card in all_cards:
        try:
            # Пытаемся найти существующий элемент инвентаря
            inventory_item = InventoryItem.objects.get(
                owner=user,
                card=card
            )
            
            # Обновляем существующий элемент
            inventory_item.quantity = random.randint(1, 5)  # Случайное количество от 1 до 5
            inventory_item.condition = random.choice(['M', 'NM', 'SP', 'MP', 'HP'])
            inventory_item.user_rating = Decimal(str(random.uniform(1.0, 10.0)))
            inventory_item.has_card = True
            inventory_item.save()
            
            updated_count += 1
            
        except InventoryItem.DoesNotExist:
            # Создаем новый элемент инвентаря
            InventoryItem.objects.create(
                owner=user,
                card=card,
                quantity=random.randint(1, 5),
                condition=random.choice(['M', 'NM', 'SP', 'MP', 'HP']),
                user_rating=Decimal(str(random.uniform(1.0, 10.0))),
                has_card=True
            )
            
            added_count += 1
        
        if (added_count + updated_count) % 100 == 0:
            print(f"✅ Обработано {added_count + updated_count} карточек...")
    
    print(f"✅ Добавлено новых элементов: {added_count}")
    print(f"✅ Обновлено существующих элементов: {updated_count}")
    print(f"📊 Всего обработано: {added_count + updated_count}")
    
    return added_count + updated_count

def add_specific_cards_to_inventory(card_numbers):
    """Добавляем конкретные карточки в инвентарь"""
    print(f"🕷️ Добавляем карточки {card_numbers} в инвентарь...")
    
    # Получаем пользователя
    user = User.objects.get(username='spiderman_collector')
    
    added_count = 0
    
    for card_number in card_numbers:
        try:
            # Находим карточку по номеру в первой серии
            card = Card.objects.get(series__number=1, number=card_number)
            
            # Проверяем, есть ли уже такой элемент в инвентаре
            try:
                existing_item = InventoryItem.objects.get(owner=user, card=card)
                print(f"ℹ️ Карточка #{card_number} уже есть в инвентаре")
                continue
            except InventoryItem.DoesNotExist:
                pass
            
            # Создаем элемент инвентаря
            InventoryItem.objects.create(
                owner=user,
                card=card,
                quantity=random.randint(1, 3),
                condition=random.choice(['M', 'NM', 'SP']),
                user_rating=Decimal(str(random.uniform(7.0, 10.0))),
                has_card=True
            )
            
            added_count += 1
            print(f"✅ Добавлена карточка #{card_number}: {card.title}")
            
        except Card.DoesNotExist:
            print(f"⚠️ Карточка #{card_number} не найдена")
    
    print(f"📊 Добавлено карточек: {added_count}")
    return added_count

def main():
    """Основная функция"""
    print("🕷️ Добавление карточек Spider-Man в инвентарь")
    
    # Добавляем все карточки
    total_count = add_cards_to_inventory()
    
    # Добавляем дополнительные популярные карточки
    popular_cards = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    popular_count = add_specific_cards_to_inventory(popular_cards)
    
    print(f"\n🎉 Добавление завершено!")
    print(f"📊 Всего элементов в инвентаре: {total_count}")
    print(f"📊 Популярных карточек добавлено: {popular_count}")
    print(f"💡 Теперь все карточки доступны в инвентаре!")

if __name__ == '__main__':
    main()
