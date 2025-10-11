# 🚀 Быстрый тест авторизации

## Проблема решена!
✅ Исправлена проблема с Telegram авторизацией
✅ Теперь после входа пользователь остается авторизованным
✅ Добавлена загрузка данных пользователя после получения токенов

## Быстрый запуск для тестирования

### 1. Запуск Backend (Терминал 1)
```bash
cd backend
source venv/bin/activate
python manage.py migrate
python manage.py runserver
```

### 2. Запуск Frontend (Терминал 2)
```bash
cd frontend
npm install  # если еще не установлены зависимости
npm run dev
```

### 3. Тестирование

#### Вариант А: Через браузер
1. Откройте http://localhost:5173/auth
2. Нажмите "🔧 Режим разработки"
3. Введите тестовые данные:
   - Telegram ID: `123456789`
   - Имя: `Тест`
   - Username: `test_user`
4. Нажмите "🚀 Войти"
5. Вы должны быть перенаправлены на `/dashboard`

#### Вариант Б: Тестовая страница
1. Откройте `test_auth.html` в браузере
2. Последовательно нажимайте кнопки:
   - "Проверить API" - убедитесь, что API работает
   - "Авторизоваться" - получите токены
   - "Получить данные пользователя" - проверьте, что токен работает

### 4. Проверка в консоли браузера (F12)

После успешной авторизации вы должны увидеть:
```javascript
// При загрузке страницы
API_BASE_URL: http://localhost:8000/api
VITE_API_URL: undefined
PROD: false

// При авторизации
POST /api/auth/telegram/ → 200 OK
GET /api/auth/me/ → 200 OK
```

### 5. Проверка localStorage

В консоли браузера выполните:
```javascript
localStorage.getItem('access_token')
localStorage.getItem('refresh_token')
```

Оба должны содержать JWT токены.

## Что было исправлено

### До:
```typescript
const login = (accessToken: string, refreshToken: string) => {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
  // user остается null!
};
```

### После:
```typescript
const login = async (accessToken: string, refreshToken: string) => {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
  
  // Загружаем данные пользователя
  const response = await apiClient.get('/auth/me/');
  setUser(response.data);  // ✅ Теперь user устанавливается!
};
```

## Troubleshooting

### Ошибка: Connection refused
- Убедитесь, что backend запущен на http://localhost:8000
- Проверьте, что нет других процессов на порту 8000

### Ошибка: CORS
- Убедитесь, что в `backend/config/settings.py` есть:
  ```python
  CORS_ALLOW_ALL_ORIGINS = True  # для разработки
  ```

### Ошибка: Database is locked
```bash
cd backend
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser  # опционально
```

### Ошибка: Module not found
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Следующие шаги

После успешного тестирования локально:

1. **Коммит изменений**:
```bash
git add .
git commit -m "Fix: Telegram authentication - load user data after login"
```

2. **Деплой**:
```bash
# Frontend на Vercel
cd frontend
npm run build
# Vercel автоматически задеплоит при push

# Backend на Render
git push origin main
# Render автоматически задеплоит
```

3. **Проверка в production**:
- Откройте https://your-app.vercel.app/auth
- Попробуйте войти
- Проверьте, что перенаправляет на dashboard

## Дополнительная информация

- 📝 Подробная документация: `TELEGRAM_AUTH_FIX.md`
- 🧪 Тестовая страница: `test_auth.html`
- 🔧 Конфигурация API: `frontend/src/api/client.ts`
- 🔐 Контекст авторизации: `frontend/src/contexts/AuthContext.tsx`

