# Исправление проблемы с Telegram авторизацией

## Проблема
После успешной авторизации через Telegram пользователь не мог войти в систему. При попытке войти происходило перенаправление обратно на страницу авторизации.

## Причина
В контексте авторизации (`AuthContext.tsx`) функция `login` только сохраняла токены в localStorage, но не загружала данные пользователя. Из-за этого состояние `user` оставалось `null`, и `isAuthenticated` возвращал `false`, что приводило к перенаправлению на страницу авторизации.

## Решение
Обновлена функция `login` в `AuthContext.tsx`:
- Теперь после сохранения токенов функция загружает данные пользователя через `/auth/me/`
- Функция стала асинхронной (`async`)
- Добавлена обработка ошибок - если загрузка пользователя не удалась, токены удаляются

## Измененные файлы

### 1. `/frontend/src/contexts/AuthContext.tsx`
- Изменен тип `login` с `void` на `Promise<void>`
- Функция `login` теперь загружает данные пользователя после сохранения токенов

### 2. `/frontend/src/pages/AuthPage.tsx`
- Добавлен `await` перед вызовом `login()`

## Как использовать

### Локальная разработка
1. Запустите backend:
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

2. Запустите frontend:
```bash
cd frontend
npm run dev
```

3. Откройте http://localhost:5173/auth

### Использование в режиме разработки
На странице авторизации есть кнопка "🔧 Режим разработки":
1. Нажмите на кнопку
2. Заполните тестовые данные:
   - Telegram ID: любое число (например, 123456789)
   - Имя: ваше тестовое имя
   - Username: опционально
3. Нажмите "🚀 Войти"

### Использование с настоящим Telegram Login Widget
1. Убедитесь, что у вас настроен Telegram бот (@cardloginbot)
2. На странице авторизации будет отображаться Telegram Login Widget
3. Нажмите на кнопку "Login via Telegram"
4. Авторизуйтесь через Telegram

## Конфигурация API

### Локальная разработка
API автоматически подключается к `http://localhost:8000/api`

### Production
API автоматически подключается к `https://cardholder.onrender.com/api`

### Настройка через переменные окружения
Создайте файл `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000/api
```

## Проверка работы
1. Откройте консоль браузера (F12)
2. При загрузке приложения вы увидите:
   ```
   API_BASE_URL: http://localhost:8000/api (или production URL)
   VITE_API_URL: undefined (или ваше значение)
   PROD: false (или true)
   ```
3. При авторизации:
   - Должен появиться запрос к `/api/auth/telegram/`
   - Затем запрос к `/api/auth/me/`
   - Перенаправление на `/dashboard`

## Backend endpoints
- `POST /api/auth/telegram/` - авторизация через Telegram
- `GET /api/auth/me/` - получение данных текущего пользователя
- `POST /api/auth/subscription/` - проверка подписки на Telegram канал

## Troubleshooting

### Проблема: CORS ошибки
**Решение**: Убедитесь, что в `backend/config/settings.py` правильно настроены `CORS_ALLOWED_ORIGINS`

### Проблема: 401 Unauthorized при запросе `/auth/me/`
**Решение**: 
- Проверьте, что токен сохраняется в localStorage
- Проверьте, что interceptor добавляет токен в заголовки

### Проблема: База данных не инициализирована
**Решение**:
```bash
cd backend
python manage.py migrate
```

### Проблема: Backend не запускается
**Решение**:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

