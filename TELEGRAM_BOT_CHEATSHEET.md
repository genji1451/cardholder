# 📝 Telegram Bot - Шпаргалка

## 🚀 Быстрые команды

### Запуск бота
```bash
cd backend
./run_telegram_bot.sh
# или
python manage.py run_telegram_bot
```

### Создание верификаций
```bash
# Все карты + QR-коды
python manage.py create_verified_cards --generate-qr

# Только серия 1
python manage.py create_verified_cards --series 1 --generate-qr

# Перезаписать существующие
python manage.py create_verified_cards --overwrite
```

### Генерация QR-кодов
```bash
# Простые QR-коды
python manage.py generate_qr_codes

# С метками для печати
python manage.py generate_qr_codes --with-labels

# Для одной карты
python manage.py generate_qr_codes --card-id 5
```

---

## 📡 API Endpoints

### Публичные (без авторизации)
```bash
# Проверить карту
GET /api/telegram-bot/verified-cards/verify/?code=ABC123
```

### Приватные (требуют JWT токен)
```bash
# Список верификаций
GET /api/telegram-bot/verified-cards/

# Создать верификацию
POST /api/telegram-bot/verified-cards/
{
  "card_id": 5,
  "owner_info": "Info",
  "notes": "Notes"
}

# Массовое создание
POST /api/telegram-bot/verified-cards/bulk_create/
{
  "card_ids": [1, 2, 3]
}

# Получить QR-код
GET /api/telegram-bot/verified-cards/5/qr_code/

# Скачать QR-код
GET /api/telegram-bot/verified-cards/5/download_qr/

# Статистика
GET /api/telegram-bot/verified-cards/statistics/

# Активировать/деактивировать
POST /api/telegram-bot/verified-cards/5/activate/
POST /api/telegram-bot/verified-cards/5/deactivate/
```

---

## 🔑 Настройка бота

### 1. Создать бота у @BotFather
```
/newbot
→ Название: "My Card Checker"
→ Username: "my_cards_bot"
→ Получить токен
```

### 2. Настроить команды
```
/setcommands
→ Выбрать бота
→ Вставить:

start - Начать работу с ботом
help - Помощь по использованию
info - Информация о системе проверки
```

### 3. Настроить .env
```env
TELEGRAM_BOT_TOKEN=123:ABC
TELEGRAM_BOT_USERNAME=my_bot
```

---

## 📁 Где что лежит

```
QR-коды:          backend/media/qr_codes/
Метки для печати: backend/media/qr_codes/labels/
Скрипт запуска:   backend/run_telegram_bot.sh
Главный код бота: backend/telegram_bot/bot.py
Утилиты QR:       backend/telegram_bot/utils.py
Модели:           backend/telegram_bot/models.py
API:              backend/telegram_bot/views.py
```

---

## 🎨 Админка Django

```
URL: http://localhost:8000/admin/

Разделы:
- Верифицированные карты: /admin/telegram_bot/verifiedcard/
- Логи проверок:         /admin/telegram_bot/verificationlog/

Возможности:
- ✅ Просмотр всех верификаций
- ✅ Создание новых
- ✅ Скачивание QR-кодов
- ✅ Просмотр статистики
- ✅ Активация/деактивация
```

---

## 🔧 Troubleshooting

### Бот не запускается
```bash
# Проверить токен
python -c "from django.conf import settings; print(settings.TELEGRAM_BOT_TOKEN)"

# Проверить зависимости
pip install python-telegram-bot qrcode[pil]

# Проверить миграции
python manage.py migrate
```

### QR-коды не генерируются
```bash
# Установить PIL
pip install Pillow

# Проверить права
ls -la backend/media/

# Создать директорию
mkdir -p backend/media/qr_codes
```

### API возвращает 403
```bash
# Получить токен
curl -X POST http://localhost:8000/api/login/ \
  -d "username=admin&password=pass"

# Использовать токен
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/telegram-bot/verified-cards/
```

---

## 📊 Полезные запросы

### Python
```python
# Найти карты без верификации
from apps.cards.models import Card
from telegram_bot.models import VerifiedCard

verified_ids = VerifiedCard.objects.values_list('card_id', flat=True)
unverified = Card.objects.exclude(id__in=verified_ids)
print(f"Карт без верификации: {unverified.count()}")

# Топ-10 популярных карт
top = VerifiedCard.objects.order_by('-verification_count')[:10]
for vc in top:
    print(f"{vc.card.title}: {vc.verification_count} проверок")

# Статистика за сегодня
from django.utils import timezone
from datetime import timedelta
today = timezone.now().date()
logs_today = VerificationLog.objects.filter(
    checked_at__date=today
).count()
print(f"Проверок сегодня: {logs_today}")
```

### Bash
```bash
# Сколько верификаций создано
python manage.py shell -c "from telegram_bot.models import VerifiedCard; print(VerifiedCard.objects.count())"

# Сколько QR-кодов
ls backend/media/qr_codes/*.png | wc -l

# Общая статистика
curl -s http://localhost:8000/api/telegram-bot/verified-cards/statistics/ | jq
```

---

## 🎯 Быстрый старт (копипаста)

```bash
# 1. Установка
cd backend
pip install python-telegram-bot qrcode[pil]

# 2. Настройка .env
echo "TELEGRAM_BOT_TOKEN=YOUR_TOKEN" >> .env
echo "TELEGRAM_BOT_USERNAME=your_bot" >> .env

# 3. Миграции
python manage.py makemigrations telegram_bot
python manage.py migrate

# 4. Создание верификаций
python manage.py create_verified_cards --generate-qr

# 5. Запуск
./run_telegram_bot.sh
```

---

## 📚 Документация

- **Быстрый старт (5 мин):** `QUICK_START_TELEGRAM_BOT.md`
- **Полная документация:** `TELEGRAM_BOT_README.md`
- **Примеры кода:** `TELEGRAM_BOT_EXAMPLES.md`
- **Итоги установки:** `TELEGRAM_BOT_SETUP_COMPLETE.md`

---

## 💡 Советы

1. **Тестируйте локально** перед production
2. **Сохраняйте QR-коды** в безопасном месте
3. **Деактивируйте карты** при возврате/обмене
4. **Мониторьте логи** на подозрительную активность
5. **Делайте backup** базы данных регулярно

---

**Версия:** 1.0  
**Дата:** 17.10.2025

