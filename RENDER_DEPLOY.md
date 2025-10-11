# 🚀 Деплой на Render и исправление 500 ошибки

## 🐛 Проблема: 500 Internal Server Error

Если вы получаете 500 ошибку при авторизации через Telegram на production:
```
POST https://cardholder.onrender.com/api/auth/telegram/ 500 (Internal Server Error)
```

## ✅ Что было исправлено

### 1. Улучшена обработка ошибок в `views.py`
- Добавлена проверка на дублирование username
- Добавлен fallback для создания профиля
- Улучшено логирование с traceback

### 2. Исправлен сигнал в `models.py`
- Сигнал `save_user_profile` теперь проверяет существование профиля
- Добавлена обработка ошибок при сохранении

---

## 📋 Шаги для деплоя

### Шаг 1: Закоммитьте изменения

```bash
cd /Users/rex/Documents/cards

git add backend/apps/core/views.py
git add backend/apps/core/models.py
git add frontend/src/contexts/AuthContext.tsx
git add frontend/src/pages/AuthPage.tsx

git commit -m "Fix: Telegram auth 500 error and improve error handling

- Added username uniqueness check
- Improved UserProfile creation with fallback
- Fixed save_user_profile signal to check profile existence
- Added detailed error logging with traceback
- Fixed login to load user data after authentication"

git push origin main
```

### Шаг 2: Проверьте деплой на Render

1. Откройте https://dashboard.render.com/
2. Найдите ваш сервис `cardholder`
3. Дождитесь завершения деплоя (статус должен стать "Live")

### Шаг 3: Проверьте логи на Render

1. В дашборде Render откройте ваш сервис
2. Перейдите на вкладку **"Logs"**
3. Проверьте последние логи:
   - Должно быть: `Starting deployment...`
   - Затем: `Build succeeded`
   - И: `Your service is live`

### Шаг 4: Запустите миграции на Render

Если миграции еще не применены, запустите их через Shell:

1. В дашборде Render откройте ваш сервис
2. Нажмите **"Shell"** в правом верхнем углу
3. Выполните команды:

```bash
# Применить миграции
python manage.py migrate

# Проверить статус
python manage.py showmigrations

# Создать суперпользователя (опционально)
python manage.py createsuperuser
```

### Шаг 5: Проверьте API endpoint

Откройте в браузере или через curl:

```bash
# Проверка API root
curl https://cardholder.onrender.com/api/

# Должен вернуть:
{
  "message": "Spider-Man Cards Collection API",
  "version": "1.0.0",
  "status": "running",
  ...
}
```

### Шаг 6: Тестирование авторизации

Откройте ваш frontend на Vercel и попробуйте авторизоваться:
1. Перейдите на страницу авторизации
2. Нажмите "🔧 Режим разработки"
3. Введите тестовые данные
4. Нажмите "🚀 Войти"

**Если все работает:**
- Вы будете перенаправлены на `/dashboard`
- В localStorage будут сохранены токены
- Пользователь будет создан в базе данных

**Если получаете ошибку:**
- Откройте консоль браузера (F12)
- Проверьте ответ сервера в Network tab
- Теперь сервер вернет детальную информацию об ошибке:
  ```json
  {
    "error": "Server error",
    "details": "...",
    "traceback": "...",
    "message": "..."
  }
  ```

---

## 🔍 Проверка логов с детальной информацией

После обновления кода, при ошибке авторизации вы получите детальную информацию:

### В консоли браузера:
```javascript
{
  "error": "Server error",
  "details": "actual error message",
  "traceback": "full Python traceback",
  "message": "user-friendly message"
}
```

### В логах Render:
```
[ERROR] Exception in telegram_auth: ...
Traceback (most recent call last):
  ...
```

---

## 🛠️ Troubleshooting

### Проблема: Деплой не запускается автоматически

**Решение:**
1. Зайдите в Settings вашего сервиса на Render
2. Проверьте "Auto-Deploy" включен
3. Или нажмите "Manual Deploy" → "Deploy latest commit"

### Проблема: Миграции не применяются автоматически

**Решение:**
Добавьте Build Command в настройках Render:
```bash
pip install -r requirements.txt && python manage.py migrate
```

Или в `render.yaml` (если используете):
```yaml
services:
  - type: web
    name: cardholder
    env: python
    buildCommand: "pip install -r requirements.txt && python manage.py migrate"
    startCommand: "gunicorn config.wsgi:application"
```

### Проблема: "no such table: core_userprofile"

**Решение:**
Миграции не применены. Запустите через Shell:
```bash
python manage.py migrate
```

### Проблема: "UNIQUE constraint failed: auth_user.username"

**Решение:**
Этот пользователь уже существует. Код теперь автоматически добавляет номер к username.

### Проблема: Все еще получаете 500 ошибку

**Действия:**
1. Проверьте логи на Render
2. Скопируйте traceback из ответа сервера
3. Проверьте, что база данных существует:
   ```bash
   # В Render Shell
   python manage.py dbshell
   .tables  # для SQLite
   \dt      # для PostgreSQL
   ```

---

## 📊 Переменные окружения на Render

Убедитесь, что установлены следующие переменные:

| Переменная | Значение | Обязательно |
|-----------|----------|-------------|
| `DJANGO_SECRET_KEY` | ваш секретный ключ | ✅ Да |
| `DJANGO_DEBUG` | `False` | ✅ Да |
| `ALLOWED_HOSTS` | `cardholder.onrender.com` | ✅ Да |
| `DATABASE_URL` | автоматически (PostgreSQL) | ⚠️ Если используете PostgreSQL |
| `TELEGRAM_BOT_TOKEN` | токен вашего бота | ✅ Да |
| `CORS_ALLOWED_ORIGINS` | `https://your-frontend.vercel.app` | ⚠️ Опционально |

---

## 🎯 Проверка после деплоя

### 1. API работает
```bash
curl https://cardholder.onrender.com/api/
# Должен вернуть JSON с информацией об API
```

### 2. Миграции применены
```bash
# В Render Shell
python manage.py showmigrations
# Все миграции должны быть отмечены [X]
```

### 3. База данных работает
```bash
# В Render Shell
python manage.py shell

>>> from apps.core.models import UserProfile
>>> UserProfile.objects.count()
0  # или количество существующих профилей
```

### 4. Авторизация работает
Попробуйте авторизоваться через frontend на Vercel.

---

## 📚 Дополнительные ресурсы

- **Render Docs:** https://render.com/docs
- **Django Deployment:** https://docs.djangoproject.com/en/4.2/howto/deployment/
- **Troubleshooting Guide:** https://render.com/docs/troubleshooting-deploys

---

## ✅ Checklist после деплоя

- [ ] Код закоммичен и запушен в GitHub
- [ ] Деплой на Render завершен (статус "Live")
- [ ] Миграции применены
- [ ] API endpoint отвечает
- [ ] Frontend на Vercel обновлен
- [ ] Авторизация работает
- [ ] Пользователи могут войти и остаться авторизованными
- [ ] Dashboard доступен после авторизации

---

**Дата:** 2025-10-11  
**Статус:** ✅ ГОТОВО К ДЕПЛОЮ

