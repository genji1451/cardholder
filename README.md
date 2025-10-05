# 🕷️ Spider-Man Cards Collection Portfolio

Современная платформа для управления коллекциями карточек Человека-Паука с авторизацией через Telegram.

## 🚀 Быстрый старт

### Локальная разработка

```bash
# Backend (Django)
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend (React + Vite)
cd frontend
npm install
npm run dev
```

### Развертывание на Vercel

1. **Подключите репозиторий к Vercel**
2. **Настройте переменные окружения:**
   - `VITE_API_URL` = `https://your-backend-url.herokuapp.com/api`
3. **Настройте Telegram бота:**
   - Откройте @BotFather
   - `/setdomain` → выберите @cardloginbot
   - Введите домен: `your-vercel-app.vercel.app`

## 🏗️ Архитектура

```
cards/
├── backend/                 # Django REST API
│   ├── apps/
│   │   ├── core/           # Авторизация, пользователи
│   │   ├── cards/          # Модели карточек
│   │   ├── inventory/      # Инвентарь пользователя
│   │   └── analytics/      # Аналитика
│   └── config/             # Настройки Django
├── frontend/               # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/    # React компоненты
│   │   ├── pages/         # Страницы приложения
│   │   ├── contexts/      # React Context (Auth)
│   │   └── api/           # API клиент
└── scripts/               # Скрипты для развертывания
```

## 🔧 Технологии

### Backend
- **Django 4.2** - веб-фреймворк
- **Django REST Framework** - API
- **PostgreSQL** - база данных (планируется)
- **JWT** - авторизация
- **Telegram Bot API** - интеграция с Telegram

### Frontend
- **React 19** - UI библиотека
- **TypeScript** - типизация
- **Vite** - сборщик
- **TanStack Query** - управление состоянием
- **React Router** - маршрутизация

## 📱 Функции

- ✅ **Авторизация через Telegram** - безопасный вход
- ✅ **Управление коллекцией** - добавление, редактирование карточек
- ✅ **Аналитика** - статистика коллекции
- ✅ **Список желаний** - отслеживание нужных карточек
- ✅ **Проверка подписки** - Premium доступ через Telegram канал
- 🔄 **Поделиться коллекцией** - публичные ссылки (в разработке)
- 🔄 **Магазин** - покупка карточек (в разработке)

## 🎨 Дизайн

- **Темная тема** с цветами Spider-Man (красный #e31937, синий #0066cc)
- **Полупрозрачная паутина** на фоне
- **Современный минималистичный** стиль
- **Адаптивный дизайн** для всех устройств

## 🔐 Безопасность

- **JWT токены** для авторизации
- **HMAC проверка** Telegram данных
- **CORS** настроен для продакшена
- **HTTPS** обязательно для Telegram Login Widget

## 📊 API Endpoints

```
POST /api/auth/telegram/     # Авторизация через Telegram
GET  /api/auth/me/          # Данные текущего пользователя
POST /api/auth/subscription/ # Проверка подписки на канал
GET  /api/cards/            # Список карточек
GET  /api/inventory/        # Инвентарь пользователя
GET  /api/analytics/        # Аналитика коллекции
```

## 🚀 Развертывание

### Vercel (Frontend)
```bash
# Автоматическое развертывание
./scripts/deploy_to_vercel.sh

# Или через Vercel CLI
vercel --prod
```

### Heroku (Backend)
```bash
# Создайте приложение на Heroku
heroku create your-backend-app

# Настройте переменные
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set TELEGRAM_CHANNEL_ID=@your_channel

# Разверните
git push heroku main
```

## 🧪 Тестирование

### Локальное тестирование
```bash
# Режим разработки (без Telegram)
https://localhost:5174/auth
# Переключитесь на "🔧 Режим разработки"

# Настоящий Telegram (требует HTTPS)
./scripts/setup_ngrok.sh
# Следуйте инструкциям для настройки @BotFather
```

### Продакшен тестирование
1. Разверните на Vercel
2. Настройте домен в @BotFather
3. Протестируйте авторизацию
4. Проверьте все функции

## 📋 TODO

- [ ] Переход на PostgreSQL
- [ ] Оптимизация производительности
- [ ] Активация всех кнопок
- [ ] Улучшение дизайна
- [ ] Функция "Поделиться коллекцией"
- [ ] Магазин карточек
- [ ] Монетизация через подписку

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в консоли браузера
2. Проверьте логи backend сервера
3. Убедитесь, что все зависимости установлены
4. Проверьте настройки CORS и домена

## 📄 Лицензия

MIT License - используйте свободно для личных и коммерческих проектов.

---

**Создано с ❤️ для коллекционеров карточек Человека-Паука** 🕷️