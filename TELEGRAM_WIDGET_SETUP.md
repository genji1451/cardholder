# 🤖 Настройка Telegram Login Widget

## 🔍 Проблема

Кнопка "Login with Telegram" не отображается на странице авторизации, хотя режим разработчика работает.

## 🎯 Причина

Telegram Login Widget требует специальной настройки бота через BotFather. Бот должен быть настроен для использования в качестве виджета авторизации.

---

## ✅ Решение: Настройка Telegram бота

### Шаг 1: Откройте BotFather в Telegram

1. Найдите в Telegram: **@BotFather**
2. Нажмите `/start`

### Шаг 2: Настройте домен для авторизации

Отправьте команду:
```
/setdomain
```

### Шаг 3: Выберите вашего бота

BotFather покажет список ваших ботов. Выберите бота `@cardloginbot` (или того, которого используете).

### Шаг 4: Укажите домены

Отправьте домены, на которых будет работать виджет:

**Для локальной разработки:**
```
localhost
```

**Для production:**
```
your-app.vercel.app
```

**Или оба сразу (разделите переносом строки):**
```
localhost
your-app.vercel.app
portfolio.cards
```

### Шаг 5: Проверка

BotFather должен ответить:
```
✅ Success! Domain(s) updated.
```

---

## 🧪 Проверка работы виджета

### 1. Откройте страницу авторизации

```
http://localhost:5173/auth
```

### 2. Переключитесь на режим Telegram

Нажмите кнопку **"🔄 Переключиться на Telegram"** (если вы в режиме разработчика)

### 3. Должна появиться кнопка

Вы должны увидеть голубую кнопку **"Log in with Telegram"**

### 4. Откройте консоль браузера (F12)

Проверьте наличие ошибок:

**Если ошибок нет** - виджет загружается правильно

**Если есть ошибка:**
```
Refused to frame 'https://oauth.telegram.org/' because an ancestor violates the following Content Security Policy directive
```
Это значит, что бот не настроен для вашего домена.

---

## 🔧 Альтернативное решение: Проверка имени бота

### Проверьте, что бот существует

1. В Telegram найдите: `@cardloginbot`
2. Если бот не найден, создайте нового:

```
/newbot
```

Следуйте инструкциям BotFather:
- Введите имя бота: `Card Login Bot`
- Введите username: `cardloginbot` (или другое доступное имя)

### Обновите имя бота в коде

Откройте `/Users/rex/Documents/cards/frontend/src/pages/AuthPage.tsx`:

```typescript
<TelegramAuth 
  onAuth={handleTelegramAuth}
  botName="cardloginbot"  // ← Замените на имя вашего бота (без @)
/>
```

---

## 🎨 Временное решение: Используйте режим разработчика

Пока не настроен Telegram Login Widget, вы можете использовать режим разработчика:

1. Откройте страницу авторизации
2. Нажмите **"🔧 Режим разработки"**
3. Введите тестовые данные
4. Войдите в систему

Режим разработчика полностью функционален и позволяет тестировать все возможности приложения.

---

## 📋 Checklist настройки

- [ ] Бот создан в BotFather
- [ ] Получен токен бота
- [ ] Настроен домен через `/setdomain`
- [ ] Домен включает `localhost` (для локальной разработки)
- [ ] Домен включает production URL (для продакшена)
- [ ] Имя бота правильно указано в `AuthPage.tsx`
- [ ] Страница перезагружена после изменений

---

## 🔍 Отладка

### Проверка загрузки скрипта

Откройте консоль браузера и выполните:

```javascript
// Проверка загрузки скрипта Telegram
const scripts = document.querySelectorAll('script[src*="telegram"]');
console.log('Telegram scripts:', scripts);

// Проверка контейнера
const container = document.getElementById('telegram-login-container');
console.log('Container:', container);
console.log('Container content:', container?.innerHTML);
```

### Ожидаемый результат:

```javascript
// Должен быть загружен скрипт
Telegram scripts: NodeList [ script ]

// Контейнер должен содержать iframe
Container: <div id="telegram-login-container">
Container content: <script src="https://telegram.org/js/telegram-widget.js?22" ...>
```

### Проверка сети

1. Откройте DevTools (F12)
2. Перейдите на вкладку **Network**
3. Перезагрузите страницу
4. Найдите запрос к `telegram-widget.js`
5. Статус должен быть **200 OK**

---

## 🌐 Настройка для production

### Для Vercel

Добавьте домены в BotFather:
```
spiderman-cards-portfolio.vercel.app
spiderman-cards-portfolio-git-main.vercel.app
portfolio.cards
```

### Для других платформ

Используйте ваш фактический домен без `https://`:
```
your-domain.com
www.your-domain.com
```

---

## 💡 Полезные команды BotFather

| Команда | Описание |
|---------|----------|
| `/mybots` | Список ваших ботов |
| `/setdomain` | Настроить домен для Login Widget |
| `/deletebot` | Удалить бота |
| `/token` | Получить токен бота |
| `/setdescription` | Установить описание бота |
| `/setuserpic` | Установить аватар бота |

---

## 📚 Дополнительная информация

- **Telegram Login Widget Docs:** https://core.telegram.org/widgets/login
- **BotFather Guide:** https://core.telegram.org/bots#botfather
- **Telegram API:** https://core.telegram.org/bots/api

---

## ✅ Результат

После правильной настройки на странице авторизации вы увидите:

1. **Заголовок:** "Войти через Telegram"
2. **Голубую кнопку:** "Log in with Telegram"
3. При нажатии откроется окно Telegram для авторизации
4. После авторизации вы будете перенаправлены на Dashboard

---

## 🔄 Если ничего не помогло

**Используйте режим разработчика:**
- Он полностью функционален
- Не требует настройки Telegram бота
- Идеален для разработки и тестирования
- Работает как локально, так и на production

**Для переключения:**
```
Нажмите "🔧 Режим разработки" на странице авторизации
```

---

**Дата:** 2025-10-11  
**Статус:** ✅ Руководство готово

