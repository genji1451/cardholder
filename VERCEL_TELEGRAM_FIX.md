# 🔧 Исправление Telegram Login на Vercel

## 🐛 Проблема

Telegram Login Widget не отображается на Vercel, хотя в режиме разработчика всё работает.

## ✅ Решение

### Шаг 1: Определите ваши домены Vercel

Vercel создаёт несколько доменов для каждого приложения:

1. **Production URL**: `your-app.vercel.app`
2. **Git branch URLs**: `your-app-git-main-username.vercel.app`
3. **Preview URLs**: `your-app-abc123.vercel.app`
4. **Custom domain** (если настроен): `portfolio.cards`

**Как узнать точный URL:**
1. Откройте ваше приложение на Vercel
2. Посмотрите в адресную строку браузера
3. Скопируйте домен (без `https://` и без пути)

Примеры:
```
spiderman-cards-portfolio.vercel.app
spiderman-cards-portfolio-git-main-rexs-projects.vercel.app
portfolio.cards
```

---

### Шаг 2: Добавьте ВСЕ домены в BotFather

1. **Откройте Telegram**
2. Найдите **@BotFather**
3. Отправьте команду:
   ```
   /setdomain
   ```

4. **Выберите вашего бота** (например, `@cardloginbot`)

5. **Отправьте ВСЕ домены** (каждый с новой строки):
   ```
   localhost
   spiderman-cards-portfolio.vercel.app
   spiderman-cards-portfolio-git-main-rexs-projects.vercel.app
   spiderman-cards-portfolio-git-main.vercel.app
   portfolio.cards
   ```

6. BotFather ответит:
   ```
   ✅ Success! Domain(s) updated.
   ```

---

### Шаг 3: Очистите кеш и перезагрузите

1. **На странице Vercel** нажмите:
   - Mac: `Cmd + Shift + R`
   - Windows/Linux: `Ctrl + Shift + R`

2. Или откройте в **режиме инкognito** для проверки

---

### Шаг 4: Проверка в консоли

Откройте **DevTools** (F12) → **Console** и проверьте:

```javascript
// 1. Проверьте текущий домен
console.log('Current domain:', window.location.hostname);

// 2. Проверьте наличие iframe
const iframe = document.querySelector('iframe[id^="telegram-login"]');
console.log('Telegram iframe:', iframe);

// 3. Проверьте src iframe
console.log('Iframe src:', iframe?.src);

// 4. Проверьте видимость
console.log('Iframe display:', window.getComputedStyle(iframe).display);
console.log('Iframe visibility:', window.getComputedStyle(iframe).visibility);
```

**Ожидаемый результат:**
```javascript
Current domain: "spiderman-cards-portfolio.vercel.app"
Telegram iframe: <iframe id="telegram-login-cardloginbot" ...>
Iframe src: "https://oauth.telegram.org/embed/..."
Iframe display: "block"
Iframe visibility: "visible"
```

---

### Шаг 5: Проверьте ошибки

В **Console** ищите ошибки:

**❌ Если видите:**
```
Refused to frame 'https://oauth.telegram.org/' because an ancestor violates 
the following Content Security Policy directive
```
**Решение:** Домен не добавлен в BotFather. Повторите Шаг 2.

**❌ Если видите:**
```
Refused to display 'https://oauth.telegram.org/' in a frame because it set 
'X-Frame-Options' to 'deny'
```
**Решение:** Домен не добавлен в BotFather. Повторите Шаг 2.

**✅ Если ошибок нет:**
Виджет должен загружаться. Проверьте CSS и видимость элементов.

---

## 🔍 Отладка проблемы с видимостью

### Проверка 1: Контейнер существует

```javascript
const container = document.getElementById('telegram-login-container');
console.log('Container:', container);
console.log('Container HTML:', container?.innerHTML);
```

### Проверка 2: Iframe загружен

```javascript
const iframe = document.querySelector('#telegram-login-container iframe');
console.log('Iframe:', iframe);
console.log('Iframe width:', iframe?.offsetWidth);
console.log('Iframe height:', iframe?.offsetHeight);
```

**Если width или height = 0:**
Проблема в CSS или iframe не загрузился.

### Проверка 3: CSS стили

```javascript
const container = document.getElementById('telegram-login-container');
const styles = window.getComputedStyle(container);
console.log('Display:', styles.display);
console.log('Visibility:', styles.visibility);
console.log('Opacity:', styles.opacity);
console.log('Position:', styles.position);
```

---

## 🎨 Возможные CSS проблемы

### Проблема 1: Контейнер скрыт

Если контейнер имеет `display: none` или `visibility: hidden`, добавьте в CSS:

```css
#telegram-login-container {
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
  min-height: 40px !important;
}

#telegram-login-container iframe {
  display: block !important;
  visibility: visible !important;
}
```

### Проблема 2: Z-index

Если кнопка "за" другими элементами:

```css
#telegram-login-container {
  position: relative;
  z-index: 9999;
}
```

---

## 📊 Проверка настроек Vercel

### 1. Content Security Policy (CSP)

Убедитесь, что в Vercel не установлены строгие CSP правила.

В `vercel.json` не должно быть блокировки iframe:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Content-Security-Policy",
          "value": "frame-ancestors 'self' https://oauth.telegram.org"
        }
      ]
    }
  ]
}
```

### 2. Environment Variables

Убедитесь, что в Vercel Settings → Environment Variables не установлено:
- `DISABLE_TELEGRAM_WIDGET=true`

---

## 🌐 Список всех возможных доменов Vercel

Добавьте в BotFather ВСЕ следующие домены:

```
localhost
127.0.0.1

# Production
spiderman-cards-portfolio.vercel.app

# Git branches
spiderman-cards-portfolio-git-main.vercel.app
spiderman-cards-portfolio-git-main-rexs-projects.vercel.app

# Custom domains (если есть)
portfolio.cards
www.portfolio.cards
```

**💡 Совет:** Telegram позволяет добавлять неограниченное количество доменов, так что добавьте все возможные варианты.

---

## 🔄 Альтернативное решение

### Используйте режим разработчика на production

Если Telegram Widget не критичен, вы можете оставить только режим разработчика:

1. Откройте `frontend/src/pages/AuthPage.tsx`
2. Измените начальное состояние:

```typescript
const [useDevMode, setUseDevMode] = useState(true); // По умолчанию режим разработчика
```

Или полностью уберите переключение:

```typescript
return (
  <div className="auth-page">
    <div className="auth-container">
      <div className="auth-logo">
        <h1>🕷️ Collection Portfolio</h1>
        <p>Управляй своими коллекциями карточек</p>
      </div>

      <div className="auth-content">
        {/* Всегда показываем режим разработчика */}
        <TelegramAuthDev onAuth={handleTelegramAuth} />
        
        {/* Убрали кнопку переключения */}
      </div>
    </div>
  </div>
);
```

---

## ✅ Checklist

- [ ] Узнал точные URL приложения на Vercel
- [ ] Открыл BotFather в Telegram
- [ ] Отправил `/setdomain`
- [ ] Добавил ВСЕ домены Vercel
- [ ] Получил подтверждение от BotFather
- [ ] Очистил кеш браузера (Ctrl+Shift+R)
- [ ] Перезагрузил страницу на Vercel
- [ ] Проверил консоль на ошибки
- [ ] Кнопка Telegram Login отображается ✅

---

## 🎯 Что делать, если не помогло

### 1. Проверьте имя бота

В `frontend/src/pages/AuthPage.tsx` должно быть правильное имя бота:

```typescript
<TelegramAuth 
  onAuth={handleTelegramAuth}
  botName="cardloginbot"  // ← Без @, только имя
/>
```

### 2. Пересоздайте бота

Если ничего не помогает:
1. Создайте нового бота через BotFather: `/newbot`
2. Получите новое имя (например, `cardauth_bot`)
3. Сразу настройте домены: `/setdomain`
4. Обновите имя в коде

### 3. Используйте режим разработчика

Режим разработчика полностью функционален и работает везде:
- Локально
- На Vercel
- На любом хостинге
- Не требует настройки бота

---

**Дата:** 2025-10-11  
**Статус:** ✅ Инструкция готова

