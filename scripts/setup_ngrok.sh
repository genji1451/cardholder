#!/bin/bash

echo "🌐 Настройка ngrok для Telegram авторизации..."

# Проверяем, что ngrok установлен
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok не установлен"
    echo "💡 Установите:"
    echo "   brew install ngrok"
    echo "   или скачайте с https://ngrok.com/"
    exit 1
fi

# Проверяем, что HTTPS сервер запущен
if ! lsof -Pi :5174 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ HTTPS сервер не запущен на порту 5174"
    echo "💡 Запустите: cd frontend && VITE_HTTPS=true npm run dev"
    exit 1
fi

echo "🚀 Запуск ngrok туннеля..."

# Запускаем ngrok в фоне
ngrok http 5174 --log=stdout > ngrok.log 2>&1 &
NGROK_PID=$!

# Ждем запуска ngrok
sleep 3

# Получаем URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
data = json.load(sys.stdin)
for tunnel in data['tunnels']:
    if tunnel['proto'] == 'https':
        print(tunnel['public_url'])
        break
")

if [ -z "$NGROK_URL" ]; then
    echo "❌ Не удалось получить ngrok URL"
    kill $NGROK_PID 2>/dev/null
    exit 1
fi

echo "✅ ngrok туннель создан!"
echo "🌐 Публичный URL: $NGROK_URL"
echo ""
echo "📋 Следующие шаги:"
echo "1. Откройте Telegram и найдите @BotFather"
echo "2. Отправьте /setdomain"
echo "3. Выберите бота @cardloginbot"
echo "4. Введите домен: $(echo $NGROK_URL | sed 's|https://||')"
echo ""
echo "🧪 Тестирование:"
echo "1. Откройте: $NGROK_URL/auth"
echo "2. Протестируйте авторизацию через Telegram"
echo ""
echo "🛑 Для остановки ngrok: kill $NGROK_PID"

# Сохраняем PID для остановки
echo $NGROK_PID > ngrok.pid
