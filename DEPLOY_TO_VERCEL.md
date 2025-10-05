# 🚀 Развертывание на Vercel для Telegram авторизации

## 📋 Предварительные требования

1. **Аккаунт Vercel** - зарегистрируйтесь на [vercel.com](https://vercel.com)
2. **GitHub репозиторий** - загрузите код на GitHub
3. **Backend на Heroku** - разверните Django backend

## 🔧 ШАГ 1: Подготовка кода

### 1.1 Создайте .env файл для продакшена:
```bash
# frontend/.env.production
VITE_API_URL=https://your-backend-url.herokuapp.com/api
```

### 1.2 Обновите API client:
Файл уже обновлен для поддержки продакшена.

### 1.3 Создайте build скрипт:
```json
{
  "scripts": {
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  }
}
```

## 🔧 ШАГ 2: Развертывание на Vercel

### 2.1 Через веб-интерфейс:
1. Зайдите на [vercel.com](https://vercel.com)
2. Нажмите "New Project"
3. Подключите GitHub репозиторий
4. Настройте:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 2.2 Через CLI:
```bash
# Установите Vercel CLI
npm i -g vercel

# Войдите в аккаунт
vercel login

# Разверните проект
cd /Users/rex/Documents/cards
vercel

# Следуйте инструкциям:
# - Set up and deploy? Y
# - Which scope? (выберите ваш аккаунт)
# - Link to existing project? N
# - What's your project's name? cards-portfolio
# - In which directory is your code located? ./frontend
```

## 🔧 ШАГ 3: Настройка переменных окружения

В Vercel Dashboard:
1. Перейдите в Settings → Environment Variables
2. Добавьте:
   - `VITE_API_URL` = `https://your-backend-url.herokuapp.com/api`

## 🔧 ШАГ 4: Настройка Telegram бота

### 4.1 Обновите домен в @BotFather:
1. Откройте @BotFather в Telegram
2. Отправьте `/setdomain`
3. Выберите бота `@cardloginbot`
4. Введите домен: `your-vercel-app.vercel.app`

### 4.2 Обновите настройки backend:
В Heroku или где развернут backend:
```bash
# Установите переменные окружения
heroku config:set TELEGRAM_BOT_TOKEN=8089087655:AAH3ZobI5iV5ZTENxyLqQdyDV5nXGfAXTU0
heroku config:set TELEGRAM_CHANNEL_ID=@cardholderka
```

## 🔧 ШАГ 5: Настройка CORS

В backend settings.py:
```python
# Разрешить домен Vercel
CORS_ALLOWED_ORIGINS = [
    'https://your-vercel-app.vercel.app',
    'http://localhost:5173',  # для разработки
]
```

## 🧪 Тестирование

### 1. Откройте сайт:
```
https://your-vercel-app.vercel.app/auth
```

### 2. Протестируйте авторизацию:
1. Убедитесь, что переключены на режим Telegram
2. Нажмите "Login with Telegram"
3. Авторизуйтесь через Telegram
4. Проверьте дашборд

### 3. Протестируйте подписку:
1. Подпишитесь на канал `@cardholderka`
2. Нажмите "Проверить" в компоненте подписки
3. Убедитесь, что статус изменился

## 🔧 Альтернатива: Использование ngrok для локального тестирования

Если не хотите развертывать на Vercel:

### 1. Установите ngrok:
```bash
brew install ngrok
# или скачайте с https://ngrok.com/
```

### 2. Запустите HTTPS туннель:
```bash
# В одном терминале
cd /Users/rex/Documents/cards/frontend
VITE_HTTPS=true npm run dev

# В другом терминале
ngrok http 5174
```

### 3. Получите публичный URL:
ngrok покажет что-то вроде:
```
https://abc123.ngrok.io -> http://localhost:5174
```

### 4. Настройте домен бота:
В @BotFather установите домен: `abc123.ngrok.io`

## 🐛 Решение проблем

### Проблема: "API не доступен"
**Решение**: 
1. Проверьте, что backend развернут и работает
2. Убедитесь, что CORS настроен правильно
3. Проверьте переменную VITE_API_URL

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
