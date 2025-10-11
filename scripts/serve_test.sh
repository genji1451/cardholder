#!/bin/bash

# Скрипт для запуска test_auth.html через локальный HTTP сервер
# Это избавит от CORS проблем с file:// протоколом

echo "🚀 Запуск локального HTTP сервера для test_auth.html..."
echo ""
echo "📝 test_auth.html будет доступен по адресу:"
echo "   http://localhost:8080/test_auth.html"
echo ""
echo "⚠️  ВАЖНО: Убедитесь, что backend запущен на http://localhost:8000"
echo ""
echo "Нажмите Ctrl+C для остановки сервера"
echo ""

# Запускаем простой HTTP сервер на порту 8080
cd "$(dirname "$0")/.."

if command -v python3 &> /dev/null; then
    python3 -m http.server 8080
elif command -v python &> /dev/null; then
    python -m http.server 8080
else
    echo "❌ Python не найден!"
    echo "Установите Python или откройте test_auth.html другим способом"
    exit 1
fi

