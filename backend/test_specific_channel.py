#!/usr/bin/env python3
"""
Тестовый скрипт для проверки отправки в конкретный канал
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
import asyncio
from telegram import Bot

async def test_specific_channel():
    """Тест отправки в конкретный канал"""
    bot_token = "8089087655:AAH3ZobI5iV5ZTENxyLqQdyDV5nXGfAXTU0"
    channel_id = "-1003230450630"  # Ваш канал
    
    print(f"\n🧪 Тестирование отправки в канал {channel_id}...")
    
    # Проверяем существование канала
    print("\n1️⃣ Проверка канала через API...")
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getChat"
        params = {"chat_id": channel_id}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                chat_info = result.get('result', {})
                print(f"   ✅ Канал найден!")
                print(f"   Название: {chat_info.get('title', 'Не указано')}")
                print(f"   ID: {chat_info.get('id')}")
                print(f"   Username: @{chat_info.get('username', 'Нет')}")
            else:
                print(f"   ❌ Канал не найден: {result.get('description')}")
                return
        else:
            print(f"   ❌ HTTP ошибка: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return
    
    # Отправляем тестовое сообщение
    print("\n2️⃣ Отправка тестового сообщения...")
    try:
        bot = Bot(token=bot_token)
        
        test_message = """🧪 <b>ТЕСТ</b>

Это тестовое сообщение в канал с ID -1003230450630

✅ Если вы видите это сообщение - канал настроен правильно!"""
        
        await bot.send_message(
            chat_id=channel_id,
            text=test_message,
            parse_mode='HTML'
        )
        print(f"   ✅ Сообщение успешно отправлено!")
        print(f"   Проверьте канал в Telegram")
        
    except Exception as e:
        print(f"   ❌ Ошибка отправки: {e}")
        error_msg = str(e)
        
        if "chat not found" in error_msg.lower():
            print(f"   💡 Канал не найден. Проверьте ID")
        elif "not enough rights" in error_msg.lower():
            print(f"   💡 Бот не имеет прав. Добавьте бота @cardloginbot как администратора")
        elif "forbidden" in error_msg.lower():
            print(f"   💡 Бот заблокирован или не добавлен в канал")
        else:
            print(f"   💡 Полная ошибка: {error_msg}")

if __name__ == "__main__":
    asyncio.run(test_specific_channel())

