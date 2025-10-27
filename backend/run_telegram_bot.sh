#!/bin/bash
# Скрипт для запуска Telegram бота

echo "🤖 Запуск Telegram бота для проверки подлинности карт..."

# Активируем виртуальное окружение если оно есть
if [ -d "venv" ]; then
    echo "📦 Активация виртуального окружения..."
    source venv/bin/activate
fi

# Проверяем наличие переменных окружения
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден!"
    echo "Создайте файл .env и добавьте TELEGRAM_BOT_TOKEN и TELEGRAM_BOT_USERNAME"
    exit 1
fi

# Запускаем бота
python manage.py run_telegram_bot

