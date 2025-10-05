# 🔧 Настройка переменных окружения в Vercel

## 🚨 ПРОБЛЕМА: CORS Error

Ваш сайт работает на `https://portfolio.cards`, но пытается подключиться к `https://your-backend-url.herokuapp.com/api`, который не настроен для CORS.

## 🔧 РЕШЕНИЕ: Настройка переменных окружения

### 1. Зайдите в Vercel Dashboard
1. Откройте [vercel.com/dashboard](https://vercel.com/dashboard)
2. Найдите ваш проект `spiderman-cards-portfolio`
3. Нажмите на проект

### 2. Настройте переменные окружения
1. Перейдите в **Settings** → **Environment Variables**
2. Добавьте новую переменную:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://your-backend-url.herokuapp.com/api`
   - **Environment**: Production, Preview, Development

### 3. Обновите Backend CORS
В вашем Django backend (Heroku) добавьте в `settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    'https://portfolio.cards',
    'https://spiderman-cards-portfolio.vercel.app',
    'https://spiderman-cards-portfolio-git-main.vercel.app',
    'http://localhost:5173',
    'http://localhost:5174',
]
```

### 4. Перезапустите приложение
После изменения переменных:
1. В Vercel Dashboard нажмите **Deployments**
2. Нажмите **Redeploy** на последнем деплое
3. Или сделайте новый коммит в GitHub

## 🔧 АЛЬТЕРНАТИВА: Использование реального Backend URL

Если у вас есть развернутый backend, замените `your-backend-url.herokuapp.com` на реальный URL.

### Примеры реальных URL:
- `https://spiderman-cards-api.herokuapp.com/api`
- `https://your-django-app.railway.app/api`
- `https://your-backend.vercel.app/api`

## 🧪 Тестирование

После настройки:
1. Откройте `https://portfolio.cards/auth`
2. Попробуйте авторизацию через Telegram
3. Проверьте консоль браузера - ошибки CORS должны исчезнуть

## 🐛 Если все еще не работает

### Проверьте:
1. ✅ Backend запущен и доступен
2. ✅ CORS настроен правильно
3. ✅ Переменные окружения установлены
4. ✅ Приложение перезапущено

### Отладка:
1. Откройте Network tab в DevTools
2. Посмотрите на запросы к API
3. Проверьте статус ответов (200, 404, 500)
4. Проверьте заголовки CORS в ответе
