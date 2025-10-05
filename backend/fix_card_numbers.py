#!/usr/bin/env python3
"""
Скрипт для исправления номеров карточек по правильному распределению:
Часть 1: 1-275
Часть 2: 276-550  
Часть 3: 551-825
"""

import os
import sys
import django

# Настройка Django
sys.path.append('/Users/rex/Documents/cards/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.cards.models import Card, Series

def fix_card_numbers():
    """Исправляем номера карточек для правильного распределения по сериям"""
    print("🕷️ Исправляем номера карточек для правильного распределения...")
    
    # Получаем серии
    series1 = Series.objects.get(number=1)
    series2 = Series.objects.get(number=2)
    series3 = Series.objects.get(number=3)
    
    # Исправляем первую серию (1-275)
    cards_series1 = Card.objects.filter(series=series1).order_by('id')
    for i, card in enumerate(cards_series1[:275], 1):
        card.number = i
        card.save()
        if i % 50 == 0:
            print(f"✅ Обработано карточек первой серии: {i}")
    
    # Исправляем вторую серию (276-550)
    cards_series2 = Card.objects.filter(series=series2).order_by('id')
    for i, card in enumerate(cards_series2[:275], 276):
        card.number = i
        card.save()
        if (i - 275) % 50 == 0:
            print(f"✅ Обработано карточек второй серии: {i - 275}")
    
    # Исправляем третью серию (551-825)
    cards_series3 = Card.objects.filter(series=series3).order_by('id')
    for i, card in enumerate(cards_series3[:275], 551):
        card.number = i
        card.save()
        if (i - 550) % 50 == 0:
            print(f"✅ Обработано карточек третьей серии: {i - 550}")
    
    print(f"✅ Исправление завершено!")
    print(f"📊 Первая серия: карточки 1-275")
    print(f"📊 Вторая серия: карточки 276-550")
    print(f"📊 Третья серия: карточки 551-825")

def main():
    """Основная функция"""
    print("🕷️ Исправление номеров карточек Spider-Man")
    fix_card_numbers()

if __name__ == '__main__':
    main()
