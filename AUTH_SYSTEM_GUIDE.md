# 🔐 Руководство по системе авторизации

## Обзор

В приложении реализованы **три способа авторизации**:
1. 📧 **Email/Логин + Пароль** (основной метод)
2. ✈️ **Telegram Widget** (для пользователей Telegram)
3. 🔧 **Dev Mode** (для разработки и тестирования)

## 📧 Email/Логин авторизация

### Регистрация

Пользователь может зарегистрироваться, указав:
- **Логин*** (минимум 3 символа, уникальный)
- **Email*** (валидный email, уникальный)
- **Пароль*** (минимум 8 символов)
- **Подтверждение пароля***
- Имя (опционально)
- Фамилия (опционально)

**Валидация на frontend:**
- Проверка уникальности выполняется на backend
- Проверка соответствия паролей
- Проверка формата email
- Проверка минимальной длины

**API endpoint:** `POST /api/auth/register/`

**Тело запроса:**
```json
{
  "username": "user123",
  "email": "user@example.com",
  "password": "securepass123",
  "password2": "securepass123",
  "first_name": "Иван",
  "last_name": "Иванов"
}
```

**Успешный ответ:**
```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com",
    "first_name": "Иван",
    "last_name": "Иванов",
    "profile": {...}
  },
  "message": "Регистрация прошла успешно"
}
```

### Вход

Пользователь может войти, используя:
- **Email ИЛИ Логин** + **Пароль**

Система автоматически определяет тип ввода (email или username) по наличию символа `@`.

**API endpoint:** `POST /api/auth/login/`

**Тело запроса:**
```json
{
  "login": "user@example.com",  // или "user123"
  "password": "securepass123"
}
```

**Успешный ответ:**
```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com",
    ...
  },
  "message": "Вход выполнен успешно"
}
```

## ✈️ Telegram авторизация

Авторизация через Telegram Widget остается доступной для пользователей Telegram.

**API endpoint:** `POST /api/auth/telegram/`

## 🏗️ Архитектура

### Backend

**Модели (`apps/core/models.py`):**
- `User` - стандартная модель Django с полями:
  - `username` - уникальный логин
  - `email` - уникальный email
  - `password` - хэш пароля
  - `first_name`, `last_name` - имя и фамилия
  
- `UserProfile` - расширенный профиль пользователя с Telegram-данными

**Сериализаторы (`apps/core/serializers.py`):**
- `RegisterSerializer` - валидация и создание нового пользователя
- `LoginSerializer` - валидация данных входа
- `UserSerializer` - сериализация данных пользователя

**Views (`apps/core/views.py`):**
- `register()` - регистрация нового пользователя
- `login()` - вход с email/username и паролем
- `telegram_auth()` - авторизация через Telegram

**URLs (`apps/core/urls.py`):**
```python
path('auth/register/', views.register)
path('auth/login/', views.login)
path('auth/telegram/', views.telegram_auth)
path('auth/me/', views.current_user)
```

### Frontend

**Компоненты:**

1. **`EmailAuth.tsx`** - компонент email/логин авторизации
   - Переключение между режимами регистрации и входа
   - Валидация форм
   - Обработка ошибок
   
2. **`AuthPage.tsx`** - главная страница авторизации
   - Переключение между методами авторизации
   - Обработка успешной авторизации
   - Редирект на dashboard

**Стили:**
- `EmailAuth.css` - стили для email-формы
- `AuthPage.css` - общие стили страницы авторизации

## 🔒 Безопасность

1. **Хэширование паролей:** используется встроенная система Django
2. **JWT токены:** `rest_framework_simplejwt`
   - Access token: 60 минут
   - Refresh token: 7 дней
3. **Валидация паролей:** Django password validators
   - Минимум 8 символов
   - Проверка на распространенные пароли
   - Проверка на схожесть с username

## 🚀 Как использовать

### Для разработки

1. Запустите backend:
```bash
cd backend
python manage.py runserver
```

2. Запустите frontend:
```bash
cd frontend
npm run dev
```

3. Откройте http://localhost:5173
4. Выберите метод авторизации "📧 Email/Логин"
5. Зарегистрируйтесь или войдите

### Для production

Убедитесь, что в `.env` файле установлены:
```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
ALLOWED_HOSTS=your-domain.com
```

## 🎨 UI/UX особенности

- **Современный дизайн** с градиентами и плавными переходами
- **Адаптивность** - работает на всех устройствах
- **Валидация в реальном времени** - ошибки показываются мгновенно
- **Понятные сообщения об ошибках** на русском языке
- **Индикаторы загрузки** - пользователь видит процесс
- **Успешные уведомления** - подтверждение действий

## 🐛 Обработка ошибок

**Backend:**
- Валидация данных с детальными сообщениями
- Обработка дубликатов username/email
- Проверка соответствия паролей
- Graceful error handling

**Frontend:**
- Отображение ошибок валидации по каждому полю
- Общие сообщения об ошибках
- Возможность повторить попытку
- Автоматическая очистка ошибок при исправлении

## 📝 Примеры использования

### JavaScript/TypeScript (Frontend)

```typescript
import apiClient from '../api/client';

// Регистрация
const register = async (userData) => {
  const response = await apiClient.post('/auth/register/', {
    username: userData.username,
    email: userData.email,
    password: userData.password,
    password2: userData.password2,
  });
  return response.data;
};

// Вход
const login = async (credentials) => {
  const response = await apiClient.post('/auth/login/', {
    login: credentials.login,  // email или username
    password: credentials.password,
  });
  return response.data;
};
```

### Python (Backend)

```python
from apps.core.serializers import RegisterSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken

# В view функции
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
```

## 🔄 Миграция существующих пользователей

Если у вас уже есть пользователи с Telegram-авторизацией:
- Они могут продолжать использовать Telegram
- При желании могут добавить email/пароль через профиль
- Все пользователи имеют общий профиль `UserProfile`

## 📊 База данных

**Таблицы:**
- `auth_user` - пользователи Django
- `core_userprofile` - расширенные профили

**Связи:**
- `UserProfile.user` → `User` (OneToOne)

## ⚙️ Настройки

**Backend (`settings.py`):**
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    # ... другие валидаторы
]
```

## 🎯 Roadmap

Планируемые улучшения:
- [ ] Восстановление пароля через email
- [ ] Email подтверждение при регистрации
- [ ] Двухфакторная аутентификация (2FA)
- [ ] OAuth2 (Google, GitHub)
- [ ] Управление сессиями
- [ ] История входов

## 💡 Советы

1. **Для тестирования** используйте Dev Mode
2. **Для production** обязательно настройте HTTPS
3. **Email сервис** - настройте SMTP для восстановления паролей (планируется)
4. **Логирование** - следите за попытками входа

## 📞 Поддержка

При возникновении проблем:
1. Проверьте консоль браузера (F12)
2. Проверьте логи Django (`python manage.py runserver`)
3. Убедитесь, что все зависимости установлены
4. Проверьте настройки CORS

---

**Версия:** 1.0  
**Дата:** Октябрь 2025  
**Автор:** Cards Portfolio Team

