# ⚡ Быстрый старт - Email авторизация

## 🎯 Что сделано

Добавлена регистрация и вход через **email и пароль** ✅

---

## 🚀 Запуск за 30 секунд

### 1. Backend
```bash
cd backend
python manage.py runserver
```

### 2. Frontend
```bash
cd frontend
npm run dev
```

### 3. Тестирование
Откройте: http://localhost:5173/auth

**Вы увидите:**
- ✈️ Telegram (старый метод)
- 📧 Email (новый метод) ⭐

---

## 🧪 Быстрый тест

### Регистрация нового пользователя

1. Нажмите на **📧 Email**
2. Выберите таб **"Регистрация"**
3. Заполните:
   ```
   Email: test@example.com
   Имя: Тест
   Фамилия: Тестов
   Пароль: SecurePass123!
   Подтвердите пароль: SecurePass123!
   ```
4. Нажмите **"Зарегистрироваться"**
5. ✅ Готово! Вы автоматически войдете в систему

### Вход существующего пользователя

1. Нажмите на **📧 Email**
2. Таб **"Вход"** уже выбран
3. Введите:
   ```
   Email: test@example.com
   Пароль: SecurePass123!
   ```
4. Нажмите **"Войти"**
5. ✅ Готово!

---

## 📍 Новые API endpoints

```
POST /api/auth/register/  - Регистрация
POST /api/auth/login/     - Вход
```

### Пример запроса (curl):
```bash
# Регистрация
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!","password2":"SecurePass123!"}'

# Логин
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'
```

---

## 🎨 UI особенности

✅ Красивый переключатель методов (Telegram/Email)  
✅ Форма с валидацией  
✅ Два режима: Вход / Регистрация  
✅ Темная тема  
✅ Адаптивный дизайн  
✅ Анимации и hover эффекты  

---

## 📁 Новые файлы

**Backend:**
- ✏️ `backend/apps/core/serializers.py` - RegisterSerializer, LoginSerializer
- ✏️ `backend/apps/core/views.py` - register(), login()
- ✏️ `backend/apps/core/urls.py` - новые URL маршруты

**Frontend:**
- ✨ `frontend/src/components/EmailAuth.tsx` (новый)
- ✨ `frontend/src/components/EmailAuth.css` (новый)
- ✏️ `frontend/src/pages/AuthPage.tsx` - обновлен
- ✏️ `frontend/src/pages/AuthPage.css` - обновлен

---

## 🔐 Требования к паролю

- Минимум 8 символов
- Не должен быть слишком распространенным
- Не должен быть полностью цифровым
- Не должен быть слишком похож на email/имя

---

## 🎯 Готово!

Теперь у вас **два метода** авторизации:

1. 🚀 **Telegram** - быстро, без регистрации
2. 📧 **Email** - классика, с регистрацией

**Оба метода** работают с одной системой JWT токенов!

---

💡 **Подробная документация:** `EMAIL_AUTH_SETUP.md`










