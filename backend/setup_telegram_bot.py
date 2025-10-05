#!/usr/bin/env python3
"""
Скрипт для настройки Telegram бота
"""

import requests
import os
from django.conf import settings

def setup_bot():
    """Настройка Telegram бота"""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    bot_name = "your_bot_username"  # Замените на имя вашего бота
    
    print(f"🤖 Настройка Telegram бота...")
    print(f"Token: {bot_token[:10]}...")
    
    # Получаем информацию о боте
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    response = requests.get(url)
    
    if response.status_code == 200:
        bot_info = response.json()
        if bot_info.get('ok'):
            bot_data = bot_info['result']
            print(f"✅ Бот найден!")
            print(f"   Имя: {bot_data.get('first_name')}")
            print(f"   Username: @{bot_data.get('username')}")
            print(f"   ID: {bot_data.get('id')}")
            
            # Обновляем настройки
            print(f"\n📝 Обновите настройки:")
            print(f"   1. В frontend/src/pages/AuthPage.tsx замените 'your_bot_username' на @{bot_data.get('username')}")
            print(f"   2. Создайте Telegram канал и добавьте бота как администратора")
            print(f"   3. Обновите TELEGRAM_CHANNEL_ID в settings.py")
            
            return bot_data
        else:
            print(f"❌ Ошибка API: {bot_info.get('description')}")
    else:
        print(f"❌ Ошибка HTTP: {response.status_code}")
        print(f"   Проверьте токен бота")
    
    return None

def test_webhook():
    """Тест webhook (для будущего использования)"""
    print(f"\n🔗 Для настройки webhook используйте:")
    print(f"   curl -X POST \"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook\" \\")
    print(f"        -H \"Content-Type: application/json\" \\")
    print(f"        -d '{{\"url\": \"https://yourdomain.com/api/telegram/webhook/\"}}'")

if __name__ == "__main__":
    import django
    import os
    import sys
    
    # Настройка Django
    sys.path.append('/Users/rex/Documents/cards/backend')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    setup_bot()
    test_webhook()
