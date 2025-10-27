# 🔄 Обновление Frontend для работы с Timeweb Backend

## 📝 Что нужно изменить после миграции backend на Timeweb

---

## 1️⃣ API Client (frontend/src/api/client.ts)

**Текущий код:**
```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api', // Использует proxy через Vercel
  headers: {
    'Content-Type': 'application/json',
  },
});
```

**Обновленный код:**
```typescript
import axios from 'axios';

// После миграции на Timeweb
const API_URL = import.meta.env.VITE_API_URL || 'https://your-timeweb-domain.com/api';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // Для CORS
});

// Перехватчик для добавления JWT токена
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default apiClient;
```

---

## 2️⃣ Environment Variables

**Создать файл:** `frontend/.env.production`

```env
VITE_API_URL=https://your-timeweb-domain.com/api
```

**Создать файл:** `frontend/.env.local` (для локальной разработки)

```env
VITE_API_URL=http://localhost:8000/api
```

---

## 3️⃣ Vercel Configuration (vercel.json)

**Текущий код:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "framework": null,
  "headers": [...],
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://cardholder.onrender.com/api/:path*"
    }
  ]
}
```

**Обновленный код:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "framework": null,
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://telegram.org; frame-src 'self' https://oauth.telegram.org; connect-src 'self' https://your-timeweb-domain.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;"
        }
      ]
    }
  ],
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-timeweb-domain.com/api/:path*"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

---

## 4️⃣ Backend CORS Settings (для справки)

**В Django settings.py уже должно быть:**

```python
CORS_ALLOWED_ORIGINS = [
    'https://your-vercel-app.vercel.app',
    'https://your-custom-domain.com',  # если есть
    'http://localhost:5173',  # для разработки
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
]

CORS_ALLOW_CREDENTIALS = False  # Для JWT не нужны credentials
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://your-timeweb-domain.com',
]
```

---

## 5️⃣ Обновление AuthContext (если нужно)

**frontend/src/contexts/AuthContext.tsx**

Обычно не требует изменений, но убедитесь что:

```typescript
// AuthContext.tsx
const login = async (accessToken: string, refreshToken: string) => {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
  
  try {
    const response = await apiClient.get('/auth/me/');
    setUser(response.data);
  } catch (error) {
    console.error('Failed to fetch user', error);
  }
};
```

---

## 6️⃣ Тестирование после изменений

### Локальное тестирование:

1. **Обновить код:**
   ```bash
   cd frontend
   npm install
   ```

2. **Запустить локально:**
   ```bash
   npm run dev
   ```

3. **Открыть:** http://localhost:5173

4. **Проверить:**
   - Открыть DevTools → Network
   - Попробовать зарегистрироваться
   - Проверить что запросы идут на Timeweb domain

### Production тестирование:

1. **Закоммитить изменения:**
   ```bash
   git add .
   git commit -m "🚀 Update API endpoint to Timeweb backend"
   git push origin main
   ```

2. **Дождаться деплоя на Vercel** (~1-2 минуты)

3. **Открыть Vercel URL**

4. **Проверить:**
   - Регистрация работает
   - Вход работает
   - Нет CORS ошибок
   - JWT токены сохраняются

---

## 7️⃣ Чеклист изменений

### Frontend файлы:

- [ ] `frontend/src/api/client.ts` - обновлен baseURL
- [ ] `frontend/.env.production` - создан с VITE_API_URL
- [ ] `frontend/.env.local` - создан для локальной разработки
- [ ] `vercel.json` - обновлен rewrites на новый домен
- [ ] `vercel.json` - обновлен CSP headers с новым доменом

### Backend настройки (на Timeweb):

- [ ] `CORS_ALLOWED_ORIGINS` - добавлен Vercel URL
- [ ] `ALLOWED_HOSTS` - добавлен Timeweb домен
- [ ] SSL сертификат установлен
- [ ] Nginx CORS headers настроены (если нужно)

### Тестирование:

- [ ] Локально frontend подключается к Timeweb backend
- [ ] Production frontend работает с Timeweb backend
- [ ] Регистрация работает
- [ ] Вход работает
- [ ] JWT токены работают
- [ ] Нет CORS ошибок в консоли
- [ ] Нет 403/500 ошибок

---

## 8️⃣ Rollback план (если что-то пойдет не так)

### Быстрый откат на Render:

1. **Вернуть vercel.json:**
   ```json
   "rewrites": [{
     "source": "/api/:path*",
     "destination": "https://cardholder.onrender.com/api/:path*"
   }]
   ```

2. **Вернуть API URL:**
   ```typescript
   const API_URL = 'https://cardholder.onrender.com/api';
   ```

3. **Закоммитить:**
   ```bash
   git add .
   git commit -m "🔙 Rollback to Render backend"
   git push origin main
   ```

---

## 9️⃣ После успешной миграции

### Можно удалить:

- [ ] Render deployment (если все работает)
- [ ] Старые environment variables на Vercel
- [ ] Упоминания Render в документации

### Обновить документацию:

- [ ] README.md - новые инструкции деплоя
- [ ] AUTH_SYSTEM_GUIDE.md - новый API URL
- [ ] QUICK_START.md - обновить endpoints

---

## 🎯 Финальная проверка

**Откройте ваш Vercel сайт и проверьте:**

1. **Network Tab:**
   - Все запросы идут на `your-timeweb-domain.com`
   - Нет ошибок 403, 500
   - Нет CORS ошибок

2. **Функциональность:**
   - ✅ Регистрация работает
   - ✅ Вход работает
   - ✅ Получение списка карт работает
   - ✅ Все другие API endpoints работают

3. **Performance:**
   - Запросы быстрые (нет cold starts)
   - Нет задержек

4. **Security:**
   - HTTPS работает
   - JWT токены передаются правильно
   - Нет утечки чувствительных данных

---

## 📞 Нужна помощь?

Если возникли проблемы:

1. **Проверить логи backend на Timeweb:**
   ```bash
   journalctl -u cardholder -f
   ```

2. **Проверить Nginx логи:**
   ```bash
   tail -f /var/log/nginx/error.log
   ```

3. **Проверить browser console:**
   - Открыть DevTools (F12)
   - Вкладка Console
   - Искать ошибки

4. **Проверить Network tab:**
   - DevTools → Network
   - Смотреть на статус коды
   - Проверить Response headers

---

**Удачи с миграцией! 🚀**

