# 📧 Email/Password Authentication - Setup Guide

## 🎉 Что добавлено

Добавлена альтернативная система регистрации и авторизации через **email и пароль**, в дополнение к существующей Telegram авторизации.

---

## 📋 Изменения

### Backend (Django)

#### 1. **Serializers** (`backend/apps/core/serializers.py`)

Добавлены новые сериализаторы:

- **`RegisterSerializer`** - для регистрации новых пользователей
  - Поля: `email`, `password`, `password2`, `first_name`, `last_name`
  - Валидация: проверка совпадения паролей, уникальности email, требования к паролю
  - Использует email как username (уникальный идентификатор)

- **`LoginSerializer`** - для входа существующих пользователей
  - Поля: `email`, `password`

#### 2. **Views** (`backend/apps/core/views.py`)

Добавлены новые API endpoints:

##### `/api/auth/register/` (POST)
Регистрация нового пользователя.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "first_name": "Иван",
  "last_name": "Иванов"
}
```

**Response (201 Created):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "email": "user@example.com",
    "first_name": "Иван",
    "last_name": "Иванов",
    "profile": {...}
  },
  "message": "Регистрация прошла успешно"
}
```

##### `/api/auth/login/` (POST)
Вход для существующего пользователя.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "email": "user@example.com",
    "first_name": "Иван",
    "last_name": "Иванов",
    "profile": {...}
  },
  "message": "Вход выполнен успешно"
}
```

**Error Response (400/401/500):**
```json
{
  "error": "Invalid credentials",
  "message": "Неверный email или пароль"
}
```

#### 3. **URLs** (`backend/apps/core/urls.py`)

```python
path('auth/register/', views.register, name='register'),
path('auth/login/', views.login, name='login'),
```

---

### Frontend (React + TypeScript)

#### 1. **EmailAuth Component** (`frontend/src/components/EmailAuth.tsx`)

Новый компонент для авторизации через email/пароль:

**Возможности:**
- Переключение между режимами "Вход" и "Регистрация"
- Валидация форм (email формат, минимум 8 символов для пароля)
- Отображение ошибок
- Состояние загрузки (disabled inputs во время запроса)
- Адаптивный дизайн
- Темная тема

**Props:**
```typescript
interface EmailAuthProps {
  onSuccess: (accessToken: string, refreshToken: string) => void;
  onError: (error: string) => void;
}
```

#### 2. **AuthPage Updates** (`frontend/src/pages/AuthPage.tsx`)

Обновленная страница авторизации:

**Новые возможности:**
- Селектор метода авторизации (Telegram ✈️ / Email 📧)
- Интеграция EmailAuth компонента
- Единая обработка ошибок для обоих методов
- Плавные переходы между методами

#### 3. **Стили** (`frontend/src/components/EmailAuth.css`, `frontend/src/pages/AuthPage.css`)

Добавлены стили для:
- Селектора методов авторизации (красивые табы)
- Форм регистрации и входа
- Адаптивного дизайна (mobile-first)
- Темной темы
- Анимаций и hover эффектов

---

## 🚀 Как использовать

### Локальная разработка

1. **Backend:**
```bash
cd backend
python manage.py runserver
```

2. **Frontend:**
```bash
cd frontend
npm run dev
```

3. Откройте `http://localhost:5173/auth`

4. Вы увидите два метода авторизации:
   - **Telegram** (✈️) - существующий метод
   - **Email** (📧) - новый метод

### Регистрация нового пользователя

1. Выберите метод **Email** (📧)
2. Нажмите на таб **"Регистрация"**
3. Заполните форму:
   - Email (обязательно)
   - Имя и Фамилия (необязательно)
   - Пароль (минимум 8 символов)
   - Подтверждение пароля
4. Нажмите **"Зарегистрироваться"**
5. После успешной регистрации вы будете автоматически перенаправлены на Dashboard

### Вход существующего пользователя

1. Выберите метод **Email** (📧)
2. Таб **"Вход"** уже выбран по умолчанию
3. Введите:
   - Email
   - Пароль
4. Нажмите **"Войти"**
5. После успешного входа вы будете перенаправлены на Dashboard

---

## 🔐 Безопасность

### Backend (Django)

1. **Валидация пароля:**
   - Используется Django `validate_password`
   - Минимум 8 символов
   - Проверка на распространенные пароли
   - Проверка на схожесть с личными данными

2. **Хеширование паролей:**
   - Django автоматически хеширует пароли через `PBKDF2` алгоритм
   - Пароли никогда не хранятся в открытом виде

3. **JWT Токены:**
   - Используется `djangorestframework-simplejwt`
   - Access token (короткая жизнь)
   - Refresh token (длинная жизнь для обновления access token)

### Frontend (React)

1. **Токены в localStorage:**
   - `access_token` - для API запросов
   - `refresh_token` - для обновления access token

2. **Автоматическая авторизация:**
   - После успешного входа/регистрации загружаются данные пользователя
   - Токен добавляется в заголовок всех API запросов

---

## 🧪 Тестирование

### Тестирование API через curl

#### Регистрация:
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "first_name": "Тест",
    "last_name": "Тестов"
  }'
```

#### Логин:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

#### Получить текущего пользователя:
```bash
# Используйте access token из ответа выше
curl http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📱 UI/UX особенности

### Селектор методов авторизации
- Красивый переключатель с иконками
- Плавная анимация при переключении
- Градиентная подсветка активного метода

### Форма Email авторизации
- Два режима в одном компоненте (Вход / Регистрация)
- Валидация на frontend (HTML5 validation)
- Disabled состояние во время загрузки
- Информативные placeholder'ы
- Подсказка о требованиях к паролю

### Адаптивность
- Mobile-first дизайн
- Двухколоночная форма на десктопе (Имя/Фамилия)
- Одноколоночная на мобильных устройствах

### Темная тема
- Полная поддержка темной темы
- Автоматическая адаптация к системным настройкам
- CSS переменные для кастомизации

---

## 🔧 Настройка на Production

### Backend (Django)

В `backend/config/settings.py` убедитесь что настроено:

```python
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### Frontend (React)

Убедитесь что `VITE_API_BASE_URL` настроена правильно:

```bash
# .env.production
VITE_API_BASE_URL=https://your-production-api.com/api
```

---

## 🐛 Возможные проблемы и решения

### Ошибка: "Пользователь с таким email уже существует"
**Решение:** Email уже зарегистрирован. Используйте "Вход" вместо "Регистрация".

### Ошибка: "Неверный email или пароль"
**Решение:** 
- Проверьте правильность email
- Проверьте правильность пароля (помните, пароли чувствительны к регистру)
- Если забыли пароль, функция восстановления пока не реализована

### Ошибка: "Пароли не совпадают"
**Решение:** При регистрации оба поля пароля должны совпадать.

### Ошибка: "This password is too short. It must contain at least 8 characters."
**Решение:** Пароль должен содержать минимум 8 символов.

### CORS ошибки на Production
**Решение:** Убедитесь что в Django settings добавлен ваш frontend домен в `CORS_ALLOWED_ORIGINS`.

---

## 📊 Что дальше?

Возможные улучшения:

1. **Восстановление пароля**
   - Email с ссылкой для сброса пароля
   - Endpoint `/auth/password-reset/`

2. **Email верификация**
   - Отправка письма с подтверждением после регистрации
   - Endpoint `/auth/verify-email/`

3. **Социальные сети**
   - Google OAuth
   - GitHub OAuth
   - VK OAuth

4. **2FA (Two-Factor Authentication)**
   - TOTP (Time-based One-Time Password)
   - SMS коды

5. **Профиль пользователя**
   - Изменение email
   - Изменение пароля
   - Удаление аккаунта

---

## ✅ Чеклист для деплоя

- [ ] Тестирование регистрации локально
- [ ] Тестирование входа локально
- [ ] Проверка валидации паролей
- [ ] Проверка JWT токенов
- [ ] Настройка переменных окружения для production
- [ ] Тестирование на production
- [ ] Проверка CORS настроек
- [ ] Проверка безопасности (HTTPS обязательно!)

---

## 📝 Примечания

- Email используется как `username` в Django User модели
- Каждый пользователь, зарегистрированный через email, автоматически получает связанный `UserProfile`
- JWT токены работают одинаково для обоих методов авторизации (Telegram и Email)
- Frontend автоматически сохраняет токены и загружает данные пользователя после успешной авторизации

---

## 🎯 Готово! 

Теперь у вас есть полноценная система авторизации с двумя методами:
1. **Telegram** - быстрый вход через Telegram бота
2. **Email/Password** - классическая регистрация/вход

Оба метода работают с одной и той же системой JWT токенов и `UserProfile` моделью!

🚀 **Успешной разработки!**










