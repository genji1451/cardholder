# 🚀 Инструкция по развертыванию на Vercel

## 📋 Предварительные требования

1. **GitHub репозиторий** - код должен быть загружен на GitHub
2. **Аккаунт Vercel** - зарегистрируйтесь на [vercel.com](https://vercel.com)
3. **Backend развернут** - Django API должен быть доступен по HTTPS

## 🔧 ШАГ 1: Настройка Vercel

### 1.1 Подключение репозитория
1. Зайдите на [vercel.com](https://vercel.com)
2. Нажмите "New Project"
3. Выберите "Import Git Repository"
4. Подключите ваш GitHub репозиторий

### 1.2 Настройка проекта
```
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

### 1.3 Переменные окружения
В Settings → Environment Variables добавьте:
```
VITE_API_URL = https://your-backend-url.herokuapp.com/api
```

## 🔧 ШАГ 2: Настройка Telegram бота

### 2.1 Настройка домена
1. Откройте Telegram и найдите @BotFather
2. Отправьте команду `/setdomain`
3. Выберите бота `@cardloginbot`
4. Введите домен: `your-vercel-app.vercel.app`

### 2.2 Проверка настроек
```
/mybots → @cardloginbot → Bot Settings → Domain
```
Должно быть: `your-vercel-app.vercel.app`

## 🔧 ШАГ 3: Настройка Backend

### 3.1 Переменные окружения (Heroku)
```bash
heroku config:set TELEGRAM_BOT_TOKEN=8089087655:AAH3ZobI5iV5ZTENxyLqQdyDV5nXGfAXTU0
heroku config:set TELEGRAM_CHANNEL_ID=@cardholderka
```

### 3.2 CORS настройки
В `backend/config/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    'https://your-vercel-app.vercel.app',
    'http://localhost:5173',  # для разработки
]
```

## 🧪 Тестирование

### 1. Откройте сайт
```
https://your-vercel-app.vercel.app/auth
```

### 2. Протестируйте авторизацию
1. Убедитесь, что переключены на режим Telegram
2. Нажмите "Login with Telegram"
3. Авторизуйтесь через Telegram
4. Проверьте дашборд с профилем пользователя

### 3. Протестируйте подписку
1. Подпишитесь на канал `@cardholderka`
2. На дашборде нажмите "Проверить" в компоненте подписки
3. Убедитесь, что статус изменился на "Подписан"

## 🐛 Решение проблем

### Проблема: "API не доступен"
**Решение**: 
1. Проверьте, что backend развернут и работает
2. Убедитесь, что CORS настроен правильно
3. Проверьте переменную VITE_API_URL в Vercel

### Проблема: "Telegram widget не загружается"
**Решение**:
1. Убедитесь, что домен настроен в @BotFather
2. Проверьте, что используете HTTPS
3. Домен должен быть публичным (не localhost)

### Проблема: "Ошибка авторизации"
**Решение**:
1. Проверьте логи backend
2. Убедитесь, что TELEGRAM_BOT_TOKEN правильный
3. Проверьте настройки CORS

## 📱 Мобильное тестирование

После развертывания на Vercel:
1. Откройте сайт на мобильном устройстве
2. Протестируйте авторизацию через Telegram
3. Проверьте все функции

## 🎯 Следующие шаги

1. ✅ Развернуть на Vercel
2. ✅ Настроить домен бота
3. ✅ Протестировать авторизацию
4. ✅ Протестировать проверку подписки
5. 🔄 Реализовать ограничения для неподписчиков

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в Vercel Dashboard
2. Проверьте логи backend
3. Убедитесь, что все переменные окружения настроены
4. Проверьте настройки домена в @BotFather
