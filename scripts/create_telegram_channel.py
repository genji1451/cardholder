#!/usr/bin/env python3
"""
Скрипт для создания и настройки Telegram канала
"""

import requests
import os
from django.conf import settings

def create_channel_instructions():
    """Инструкции по созданию Telegram канала"""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    
    print(f"📺 Создание Telegram канала для тестирования...")
    print(f"")
    print(f"📋 ИНСТРУКЦИИ:")
    print(f"")
    print(f"1. Откройте Telegram")
    print(f"2. Создайте новый канал:")
    print(f"   - Название: 'Spider-Man Cards Collection'")
    print(f"   - Описание: 'Канал для коллекционеров карточек Человека-Паука'")
    print(f"   - Тип: Публичный канал")
    print(f"   - Username: @spiderman_cards_collection")
    print(f"")
    print(f"3. Добавьте бота как администратора:")
    print(f"   - Найдите бота @cardloginbot")
    print(f"   - Добавьте его в канал")
    print(f"   - Дайте права администратора")
    print(f"")
    print(f"4. Получите ID канала:")
    print(f"   - Перешлите любое сообщение из канала боту @userinfobot")
    print(f"   - Скопируйте ID канала")
    print(f"")
    print(f"5. Обновите настройки в settings.py:")
    print(f"   TELEGRAM_CHANNEL_ID = '@spiderman_cards_collection'")
    print(f"   # или используйте ID: TELEGRAM_CHANNEL_ID = '-1001234567890'")
    print(f"")
    print(f"🔧 АЛЬТЕРНАТИВА - создать тестовый канал через API:")
    
    # Попробуем создать канал через API (если бот имеет права)
    try:
        url = f"https://api.telegram.org/bot{bot_token}/createChannel"
        data = {
            "title": "Spider-Man Cards Test",
            "description": "Test channel for card collection app"
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                channel_info = result.get('result', {})
                print(f"✅ Канал создан через API!")
                print(f"   Название: {channel_info.get('title')}")
                print(f"   ID: {channel_info.get('id')}")
                print(f"   Username: @{channel_info.get('username', 'Нет')}")
            else:
                print(f"❌ Не удалось создать канал через API: {result.get('description')}")
                print(f"   Используйте ручное создание канала")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            print(f"   Используйте ручное создание канала")
            
    except Exception as e:
        print(f"❌ Ошибка API: {e}")
        print(f"   Используйте ручное создание канала")

def test_bot_in_channel():
    """Тест бота в канале"""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    channel_id = settings.TELEGRAM_CHANNEL_ID
    
    print(f"\n🧪 Тестирование бота в канале...")
    
    if channel_id == "@your_channel_username":
        print(f"❌ Канал не настроен в settings.py")
        return
    
    try:
        # Получаем информацию о канале
        url = f"https://api.telegram.org/bot{bot_token}/getChat"
        params = {"chat_id": channel_id}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                chat_info = result.get('result', {})
                print(f"✅ Канал найден!")
                print(f"   Название: {chat_info.get('title')}")
                print(f"   ID: {chat_info.get('id')}")
                print(f"   Username: @{chat_info.get('username', 'Нет')}")
                print(f"   Тип: {chat_info.get('type')}")
            else:
                print(f"❌ Канал не найден: {result.get('description')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")

if __name__ == "__main__":
    import django
    import sys
    
    # Настройка Django
    sys.path.append('/Users/rex/Documents/cards/backend')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    create_channel_instructions()
    test_bot_in_channel()
