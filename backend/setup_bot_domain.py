#!/usr/bin/env python3
"""
Скрипт для настройки домена Telegram бота
"""

import requests
import os
from django.conf import settings

def setup_bot_domain():
    """Настройка домена для Telegram бота"""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    
    print(f"🌐 Настройка домена для Telegram бота...")
    
    # Для разработки используем localhost
    # В продакшене нужно будет использовать реальный домен
    domain = "localhost:5173"  # Frontend домен
    
    # Настраиваем домен для бота
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
    # Для разработки отключаем webhook (используем polling)
    webhook_url = ""  # Пустой URL отключает webhook
    
    data = {
        "url": webhook_url,
        "allowed_updates": ["message", "callback_query"]
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print(f"✅ Webhook настроен успешно!")
                print(f"   Webhook URL: {result.get('result', {}).get('url', 'Отключен')}")
                print(f"   Pending updates: {result.get('result', {}).get('pending_update_count', 0)}")
            else:
                print(f"❌ Ошибка API: {result.get('description')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            print(f"   Ответ: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def get_bot_info():
    """Получить информацию о боте"""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                webhook_info = result.get('result', {})
                print(f"\n📊 Информация о webhook:")
                print(f"   URL: {webhook_info.get('url', 'Не настроен')}")
                print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
                print(f"   Last error: {webhook_info.get('last_error_message', 'Нет')}")
                print(f"   Last error date: {webhook_info.get('last_error_date', 'Нет')}")
            else:
                print(f"❌ Ошибка получения информации: {result.get('description')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка получения информации: {e}")

def setup_bot_commands():
    """Настройка команд бота"""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    
    commands = [
        {"command": "start", "description": "Начать работу с ботом"},
        {"command": "help", "description": "Показать помощь"},
        {"command": "auth", "description": "Авторизация в приложении"},
        {"command": "status", "description": "Проверить статус подписки"}
    ]
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/setMyCommands"
        data = {"commands": commands}
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print(f"✅ Команды бота настроены!")
                for cmd in commands:
                    print(f"   /{cmd['command']} - {cmd['description']}")
            else:
                print(f"❌ Ошибка настройки команд: {result.get('description')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка настройки команд: {e}")

if __name__ == "__main__":
    import django
    import sys
    
    # Настройка Django
    sys.path.append('/Users/rex/Documents/cards/backend')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    print(f"🤖 Настройка Telegram бота для разработки...")
    setup_bot_domain()
    get_bot_info()
    setup_bot_commands()
    
    print(f"\n📝 Инструкции:")
    print(f"   1. Откройте Telegram и найдите бота @cardloginbot")
    print(f"   2. Нажмите /start для начала работы")
    print(f"   3. Перейдите на http://localhost:5173/auth")
    print(f"   4. Нажмите кнопку 'Login with Telegram'")
    print(f"   5. Авторизуйтесь через Telegram")
