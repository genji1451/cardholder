#!/bin/bash

# Скрипт для настройки HTTPS в локальной разработке

echo "🔒 Настройка HTTPS для Telegram авторизации..."

# Создаем директорию для сертификатов
mkdir -p certificates

# Генерируем самоподписанный сертификат
echo "📜 Генерируем самоподписанный сертификат..."
openssl req -x509 -newkey rsa:4096 -keyout certificates/key.pem -out certificates/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

if [ $? -eq 0 ]; then
    echo "✅ Сертификат создан успешно!"
    echo "📁 Файлы:"
    echo "   - certificates/cert.pem (сертификат)"
    echo "   - certificates/key.pem (приватный ключ)"
    echo ""
    echo "🚀 Теперь можно запустить HTTPS сервер:"
    echo "   npm run dev:https"
else
    echo "❌ Ошибка создания сертификата"
    echo "💡 Убедитесь, что OpenSSL установлен:"
    echo "   brew install openssl"
fi
