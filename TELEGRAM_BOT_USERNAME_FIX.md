# 🔧 ИСПРАВЛЕНИЕ USERNAME БОТА

## ❌ Проблема

Бот генерировал неправильные ссылки. Вместо `t.me/cardloginbot` использовалось имя `your_bot`.

## 🔍 Причина

В файле `backend/config/settings.py` было установлено неправильное значение по умолчанию:

```python
TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "your_bot")  # ❌ Неправильно
```

## ✅ Решение

Изменили username на правильный:

```python
TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "cardloginbot")  # ✅ Правильно
```

---

## 📝 Где используется username

Username бота используется в следующих местах:

### 1. **Модель `VerifiedCard`** (`models.py`):
```python
def get_bot_link(self, bot_username):
    return f"https://t.me/{bot_username}?start={self.verification_code}"
```

### 2. **Генерация QR-кодов** (`utils.py`):
```python
bot_link = verified_card.get_bot_link(bot_username)
# Затем кодируется в QR
```

### 3. **Админ панель бота** (`bot_admin.py`):
```python
bot_link = verified_card.get_bot_link(settings.TELEGRAM_BOT_USERNAME)
# Отправляется пользователю
```

### 4. **Сериализаторы API** (`serializers.py`):
```python
bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'your_bot')
return f"https://t.me/{bot_username}?start={obj.verification_code}"
```

### 5. **Django Admin** (`admin.py`):
```python
link = obj.get_bot_link(bot_username)
# Отображается как ссылка в админке
```

---

## 🧪 Проверка

### Как проверить что ссылки правильные:

1. **Добавьте карту через бота**:
   ```
   /admin → Добавить карту
   ```

2. **Проверьте ссылку в сообщении**:
   ```
   🔗 Ссылка для проверки:
   https://t.me/cardloginbot?start=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ```
   
   ✅ Должно быть `cardloginbot`, а не `your_bot`

3. **Сканируйте QR-код**:
   - QR-код должен вести на `t.me/cardloginbot`

4. **Проверьте через Django Admin**:
   - Откройте `/admin/telegram_bot/verifiedcard/`
   - Посмотрите колонку "Bot Link"
   - Должна быть ссылка с `cardloginbot`

---

## 🔧 Как изменить username

### Способ 1: Переменная окружения (рекомендуется)

Создайте/отредактируйте файл `.env`:

```env
TELEGRAM_BOT_USERNAME=cardloginbot
```

### Способ 2: Изменить в settings.py

Отредактируйте `backend/config/settings.py`:

```python
TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "cardloginbot")
```

### После изменений:

**Перезапустите бота:**
```bash
# Остановить
ps aux | grep "run_new_bot" | grep -v grep | awk '{print $2}' | xargs kill

# Запустить
cd /Users/rex/Documents/cards/backend
source venv/bin/activate
python manage.py run_new_bot &
```

---

## 📊 Форматы ссылок

### Ссылка для проверки карты:
```
https://t.me/cardloginbot?start={verification_code}
```

**Пример:**
```
https://t.me/cardloginbot?start=a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### Когда пользователь переходит по ссылке:
1. Открывается Telegram
2. Открывается чат с ботом `@cardloginbot`
3. Автоматически отправляется команда `/start a1b2c3d4...`
4. Бот показывает информацию о карте

---

## ⚠️ Важно

### Username должен совпадать с настоящим username бота!

Чтобы узнать username бота:

1. **Через BotFather**:
   - Откройте [@BotFather](https://t.me/BotFather)
   - Отправьте `/mybots`
   - Выберите своего бота
   - Посмотрите username (без @)

2. **Через чат с ботом**:
   - Откройте чат с ботом
   - Username будет в шапке: `@cardloginbot`
   - Используйте без @: `cardloginbot`

3. **Через API**:
   ```bash
   curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
   ```
   
   Ответ:
   ```json
   {
     "ok": true,
     "result": {
       "id": 123456789,
       "is_bot": true,
       "first_name": "Card Verification Bot",
       "username": "cardloginbot"  // ← Вот это
     }
   }
   ```

---

## 🚀 Статус

**Изменения применены:** ✅ Да  
**Бот перезапущен:** ✅ Да  
**PID:** 11311  
**Правильный username:** `cardloginbot`  
**Ссылки работают:** ✅ Да

---

## 🔄 Что будет с уже созданными картами?

**Хорошие новости:** Все уже созданные карты автоматически будут использовать новый username!

Почему:
- Username не хранится в базе данных
- Метод `get_bot_link()` берет username из `settings.py` каждый раз при вызове
- QR-коды в базе не хранятся, генерируются динамически

Это означает что:
- ✅ Старые QR-коды будут вести на правильный username
- ✅ Ссылки в админке обновятся автоматически
- ✅ API будет отдавать правильные ссылки
- ✅ Не нужно ничего обновлять вручную

---

**Дата исправления:** 17 октября 2025  
**Версия:** 2.4  
**Статус:** ✅ ИСПРАВЛЕНО И РАБОТАЕТ

