# 🔧 Исправление 404 ошибки на Vercel

## 🐛 Проблема

При обновлении страницы (F5) на любом маршруте (например `/auth`, `/dashboard`) появляется **404 Not Found**.

## 🎯 Причина

Это классическая проблема **Single Page Application (SPA)**:

1. React Router обрабатывает роутинг на **клиенте**
2. Когда пользователь обновляет страницу или открывает URL напрямую, браузер делает запрос к серверу
3. Vercel пытается найти файл `/auth` или `/dashboard` на сервере
4. Эти файлы не существуют физически - есть только `index.html`
5. **Результат:** 404 Not Found

**Решение:** Все запросы должны перенаправляться на `index.html`, а React Router будет обрабатывать маршруты.

---

## ✅ Что было исправлено

### 1. Обновлен `vercel.json`

**Стало:**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://cardholder.onrender.com/api/$1"
    },
    {
      "handle": "filesystem"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

**Изменения:**
- ✅ Настроен `builds` для монорепозитория
- ✅ Указан путь к `frontend/package.json`
- ✅ Настроен `distDir: "dist"` (относительно frontend/)
- ✅ Использованы `routes` вместо `rewrites` для лучшей совместимости
- ✅ Добавлен `handle: "filesystem"` для корректной работы статических файлов

### 2. Обновлен `frontend/package.json`

Добавлен скрипт `vercel-build`:
```json
{
  "scripts": {
    "build": "tsc -b && vite build",
    "vercel-build": "npm run build"
  }
}
```

Vercel автоматически вызывает `vercel-build` при деплое.

### 3. Проверен `_redirects`

Файл `frontend/public/_redirects` уже правильно настроен:
```
/*    /index.html   200
```

Это fallback для случаев, когда Vercel не обрабатывает rewrites.

---

## 🚀 Деплой

### Шаг 1: Закоммитьте изменения

```bash
git add vercel.json frontend/package.json
git commit -m "Fix: 404 error on page refresh - configure monorepo build for Vercel"
git push origin main
```

### Шаг 2: Дождитесь деплоя

- Откройте https://vercel.com/dashboard
- Найдите ваш проект
- Дождитесь завершения деплоя (1-2 минуты)

### Шаг 3: Проверьте

1. Откройте ваш URL на Vercel
2. Перейдите на `/auth`
3. Нажмите **F5** (обновить страницу)
4. ✅ Страница должна загрузиться без 404

---

## 🔍 Как это работает

### До исправления:
```
Пользователь → /auth → F5
    ↓
Браузер запрашивает: https://your-app.vercel.app/auth
    ↓
Vercel ищет файл: /auth (не находит)
    ↓
❌ 404 Not Found
```

### После исправления:
```
Пользователь → /auth → F5
    ↓
Браузер запрашивает: https://your-app.vercel.app/auth
    ↓
Vercel rewrite: /auth → /index.html (200 OK)
    ↓
index.html загружается с React + React Router
    ↓
React Router видит путь /auth
    ↓
✅ Отображается страница AuthPage
```

---

## 📋 Маршруты приложения

После исправления все эти маршруты будут работать при прямом доступе и обновлении:

| Маршрут | Компонент | Доступ |
|---------|-----------|--------|
| `/` | HomePage | Публичный |
| `/auth` | AuthPage | Публичный |
| `/dashboard` | Dashboard | Защищенный |
| `/portfolio` | SimplePortfolio | Защищенный |
| `/catalog` | CatalogGrid | Защищенный |
| `/inventory` | InventoryGrid | Защищенный |
| `/wishlist` | WishlistPage | Защищенный |
| `/analytics` | AnalyticsPage | Защищенный |

**Защищенные маршруты:** Если пользователь не авторизован, `ProtectedRoute` перенаправит на `/auth`.

---

## 🧪 Тестирование

### Тест 1: Прямой доступ к маршрутам

```
1. Откройте новую вкладку
2. Введите: https://your-app.vercel.app/auth
3. ✅ Должна открыться страница авторизации (не 404)
```

### Тест 2: Обновление страницы

```
1. Перейдите на /dashboard
2. Нажмите F5 (обновить)
3. ✅ Страница должна загрузиться (не 404)
```

### Тест 3: История браузера

```
1. Перейдите: / → /auth → /dashboard
2. Нажмите "Назад" в браузере
3. ✅ Должна открыться предыдущая страница
4. Нажмите F5
5. ✅ Страница должна перезагрузиться (не 404)
```

### Тест 4: Закладки

```
1. Добавьте /dashboard в закладки
2. Закройте браузер
3. Откройте закладку
4. ✅ Должна открыться страница (не 404)
   (если не авторизован → перенаправит на /auth)
```

---

## 🛠️ Troubleshooting

### Проблема: Всё ещё 404 после деплоя

**Проверьте:**

1. **Деплой завершен?**
   - Откройте Vercel Dashboard
   - Проверьте статус последнего деплоя: должен быть "Ready"

2. **Кеш браузера**
   - Очистите кеш: Ctrl+Shift+R (Windows) или Cmd+Shift+R (Mac)
   - Или откройте в режиме инкognito

3. **Правильный outputDirectory**
   ```bash
   # Проверьте, что после билда есть файлы в frontend/dist/
   ls -la frontend/dist/
   # Должен быть index.html
   ```

4. **Vercel Settings**
   - Откройте Settings → General
   - Проверьте "Root Directory": должно быть пусто или `/`
   - "Output Directory" в UI Vercel не трогайте, `vercel.json` имеет приоритет

### Проблема: 404 только на определенных маршрутах

**Решение:**
Проверьте что в `vercel.json` rewrite для `/(.*)`  идет **ПОСЛЕДНИМ**:
```json
"rewrites": [
  {
    "source": "/api/(.*)",
    "destination": "https://cardholder.onrender.com/api/$1"
  },
  {
    "source": "/(.*)",  // ← Это должно быть последним!
    "destination": "/index.html"
  }
]
```

### Проблема: API запросы тоже идут на index.html

**Решение:**
Убедитесь что `/api/(.*)` rewrite идет **ПЕРЕД** `/(.*)`

---

## 📊 Сравнение конфигураций

### ❌ Неправильная конфигурация
```json
{
  "builds": [...],  // Устаревший подход
  "routes": [...]   // Тоже устаревший
}
```

### ✅ Правильная конфигурация (2024+)
```json
{
  "buildCommand": "...",
  "outputDirectory": "...",
  "rewrites": [...]
}
```

---

## 🔗 Дополнительные ресурсы

- **Vercel SPA Configuration:** https://vercel.com/docs/projects/project-configuration
- **React Router + Vercel:** https://reactrouter.com/en/main/guides/deploying
- **Vercel Rewrites:** https://vercel.com/docs/edge-network/rewrites

---

## ✅ Checklist

- [x] Обновлен `vercel.json` с правильной конфигурацией
- [x] Убрана устаревшая секция `builds`
- [x] Добавлен `buildCommand` и `outputDirectory`
- [x] Rewrites настроены правильно
- [x] Файл `_redirects` уже существует
- [ ] Изменения закоммичены
- [ ] Задеплоено на Vercel
- [ ] Протестированы все маршруты
- [ ] Обновление страницы работает ✅

---

**Дата:** 2025-10-11  
**Статус:** ✅ Готово к деплою

