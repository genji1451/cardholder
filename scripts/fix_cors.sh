#!/bin/bash

echo "🔧 Исправление CORS ошибки..."

# Обновляем CORS настройки в backend
echo "📝 Обновляем CORS настройки в backend..."

# Создаем временный файл с обновленными настройками
cat > backend_cors_fix.py << 'EOF'
# Добавьте эти настройки в backend/config/settings.py

CORS_ALLOWED_ORIGINS = [
    'https://portfolio.cards',
    'https://spiderman-cards-portfolio.vercel.app',
    'https://spiderman-cards-portfolio-git-main.vercel.app',
    'http://localhost:5173',
    'http://localhost:5174',
]

# Также добавьте эти заголовки
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_CREDENTIALS = True
EOF

echo "✅ CORS настройки готовы"
echo ""
echo "📋 Следующие шаги:"
echo "1. Обновите backend/config/settings.py с настройками выше"
echo "2. Перезапустите backend сервер"
echo "3. В Vercel Dashboard добавьте переменную:"
echo "   VITE_API_URL = https://your-backend-url.herokuapp.com/api"
echo "4. Перезапустите приложение в Vercel"
echo ""
echo "🧪 Тестирование:"
echo "1. Откройте https://portfolio.cards/auth"
echo "2. Попробуйте авторизацию"
echo "3. Проверьте консоль браузера"
