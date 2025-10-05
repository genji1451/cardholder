#!/bin/bash

echo "🚀 Развертывание на Vercel для Telegram авторизации..."

# Проверяем, что Vercel CLI установлен
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI не установлен"
    echo "💡 Установите: npm i -g vercel"
    exit 1
fi

# Проверяем, что мы в правильной директории
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Не найдена директория frontend"
    echo "💡 Запустите скрипт из корневой директории проекта"
    exit 1
fi

echo "📦 Подготовка к развертыванию..."

# Создаем .env файл для продакшена
cat > frontend/.env.production << EOF
VITE_API_URL=https://your-backend-url.herokuapp.com/api
EOF

echo "✅ .env.production создан"

# Проверяем, что пользователь авторизован в Vercel
if ! vercel whoami &> /dev/null; then
    echo "🔐 Авторизация в Vercel..."
    vercel login
fi

echo "🚀 Развертывание на Vercel..."

# Развертываем проект
vercel --prod

echo ""
echo "✅ Развертывание завершено!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Скопируйте URL вашего приложения"
echo "2. Настройте домен в @BotFather:"
echo "   /setdomain -> выберите @cardloginbot -> введите ваш URL"
echo "3. Обновите VITE_API_URL в настройках Vercel"
echo "4. Протестируйте авторизацию"
echo ""
echo "🔗 Полезные ссылки:"
echo "- Vercel Dashboard: https://vercel.com/dashboard"
echo "- Telegram Bot: @BotFather"
echo "- Ваш канал: @cardholderka"
