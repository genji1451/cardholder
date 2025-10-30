#!/usr/bin/env python3
"""
Тестовый скрипт для проверки отправки сообщений в Telegram канал
"""

import os
import sys
import django

# Настраиваем Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
import requests
import asyncio
from telegram import Bot

async def test_send_message():
    """Тест отправки сообщения в канал"""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    channel_id = settings.TELEGRAM_CHANNEL_ID
    
    print(f"\n🧪 Тестирование отправки сообщения в Telegram канал...")
    print(f"Bot token: {bot_token[:10] if bot_token else 'None'}...")
    print(f"Channel ID: {channel_id}")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN не настроен")
        return
    
    if not channel_id:
        print("❌ TELEGRAM_CHANNEL_ID не настроен")
        return
    
    # Сначала проверяем доступ к каналу через API
    print("\n1️⃣ Проверка доступа к каналу через REST API...")
    
    # Пробуем проверить username
    test_channel_id = "@cardholderka"
    print(f"   Пробуем username: {test_channel_id}")
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getChat"
        params = {"chat_id": test_channel_id}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                chat_info = result.get('result', {})
                print(f"   ✅ Канал найден через username!")
                print(f"   Название: {chat_info.get('title', 'Не указано')}")
                print(f"   ID: {chat_info.get('id')}")
                print(f"   Username: @{chat_info.get('username', 'Нет')}")
                print(f"   Тип: {chat_info.get('type')}")
                
                # Теперь пробуем числовой ID
                numeric_id = chat_info.get('id')
                if numeric_id:
                    print(f"\n   Проверяем числовой ID: {numeric_id}")
                    params = {"chat_id": numeric_id}
                    response = requests.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('ok'):
                            print(f"   ✅ Числовой ID тоже работает!")
                        else:
                            print(f"   ❌ Числовой ID не работает: {result.get('description')}")
            else:
                print(f"   ❌ Канал не найден: {result.get('description')}")
                return
        else:
            print(f"   ❌ HTTP ошибка: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Ошибка проверки канала: {e}")
        return
    
    # Проверяем, является ли бот администратором
    print("\n2️⃣ Проверка прав бота в канале...")
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getChatMember"
        params = {
            "chat_id": channel_id,
            "user_id": bot_token.split(':')[0]  # Используем первую часть токена как user_id
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                member_info = result.get('result', {})
                print(f"   ✅ Бот найден в канале")
                print(f"   Статус: {member_info.get('status')}")
                if member_info.get('status') in ['administrator', 'creator']:
                    print(f"   ✅ Бот имеет права администратора")
                else:
                    print(f"   ⚠️  Бот НЕ является администратором!")
                    print(f"   Нужно добавить бота как администратора с правами отправки сообщений")
        else:
            print(f"   ❌ HTTP ошибка: {response.status_code}")
            print(f"   Это нормально, если используется числовой ID канала")
    except Exception as e:
        print(f"   ⚠️  Ошибка проверки прав: {e}")
        print(f"   Продолжаем тест отправки сообщения...")
    
    # Пробуем отправить тестовое сообщение
    print("\n3️⃣ Попытка отправить тестовое сообщение...")
    
    # Сначала пробуем отправить через username
    test_message = """🧪 <b>Тестовое сообщение</b>

Это тестовое сообщение для проверки работы уведомлений о заказах.

Если вы видите это сообщение, значит бот настроен правильно! ✅"""
    
    try:
        bot = Bot(token=bot_token)
        
        # Пробуем username
        print("   Пробуем отправить через username: @cardholderka")
        try:
            await bot.send_message(
                chat_id="@cardholderka",
                text=test_message,
                parse_mode='HTML'
            )
            print(f"   ✅ Тестовое сообщение успешно отправлено через username!")
            print(f"   Проверьте канал в Telegram")
            return
        except Exception as e_username:
            print(f"   ❌ Ошибка через username: {e_username}")
        
        # Если не сработало, пробуем числовой ID из настроек
        print(f"   Пробуем отправить через числовой ID: {channel_id}")
        await bot.send_message(
            chat_id=channel_id,
            text=test_message,
            parse_mode='HTML'
        )
        print(f"   ✅ Тестовое сообщение успешно отправлено через числовой ID!")
        print(f"   Проверьте канал в Telegram")
        
    except Exception as e:
        print(f"   ❌ Ошибка отправки сообщения: {e}")
        error_msg = str(e)
        
        if "chat not found" in error_msg.lower():
            print(f"   💡 Решение: Канал не найден. Проверьте правильность ID канала")
        elif "not enough rights" in error_msg.lower():
            print(f"   💡 Решение: Бот не имеет прав для отправки сообщений")
            print(f"   Добавьте бота как администратора с правами 'Отправлять сообщения'")
        elif "forbidden" in error_msg.lower():
            print(f"   💡 Решение: Бот заблокирован в канале или не добавлен")
            print(f"   Убедитесь, что бот @{settings.TELEGRAM_BOT_USERNAME} добавлен в канал")
        else:
            print(f"   💡 Полная ошибка: {error_msg}")
    
    print("\n" + "="*60)
    print("📋 ИНСТРУКЦИЯ ПО НАСТРОЙКЕ:")
    print("="*60)
    print("\n1. Откройте ваш Telegram канал")
    print("2. Перейдите в 'Настройки канала' → 'Администраторы'")
    print(f"3. Нажмите 'Добавить администратора'")
    print(f"4. Найдите бота @{settings.TELEGRAM_BOT_USERNAME}")
    print("5. Добавьте его и дайте право 'Отправлять сообщения'")
    print("6. Остальные права можно отключить")
    print("7. Запустите этот скрипт снова для проверки\n")

if __name__ == "__main__":
    asyncio.run(test_send_message())

