# Telegram Bot для проверки подлинности карт

## Быстрый запуск

```bash
# Установка зависимостей
pip install python-telegram-bot qrcode[pil]

# Настройка .env
echo "TELEGRAM_BOT_TOKEN=YOUR_TOKEN" >> ../.env
echo "TELEGRAM_BOT_USERNAME=your_bot" >> ../.env

# Миграции
python ../manage.py makemigrations telegram_bot
python ../manage.py migrate

# Создание верификаций
python ../manage.py create_verified_cards --generate-qr

# Запуск бота
python ../manage.py run_telegram_bot
# или напрямую:
python bot.py
```

## Структура

```
telegram_bot/
├── bot.py              # Основной код Telegram бота
├── models.py           # VerifiedCard, VerificationLog
├── utils.py            # Генерация QR-кодов
├── views.py            # REST API endpoints
├── serializers.py      # DRF сериализаторы
├── urls.py             # URL маршруты
├── admin.py            # Django admin
├── tests.py            # Тесты
└── management/
    └── commands/
        ├── run_telegram_bot.py
        ├── create_verified_cards.py
        └── generate_qr_codes.py
```

## Модели

### VerifiedCard
- `card` - ForeignKey к Card
- `verification_code` - Уникальный UUID
- `is_active` - Активна ли карта
- `verification_count` - Количество проверок
- `owner_info` - Информация о владельце
- `notes` - Примечания

### VerificationLog
- `verified_card` - Какая карта проверена
- `telegram_user_id` - ID пользователя Telegram
- `telegram_username` - Username
- `checked_at` - Время проверки
- `ip_address` - IP адрес

## API

```
GET    /api/telegram-bot/verified-cards/
POST   /api/telegram-bot/verified-cards/
GET    /api/telegram-bot/verified-cards/{id}/
GET    /api/telegram-bot/verified-cards/verify/?code=XXX
GET    /api/telegram-bot/verified-cards/{id}/qr_code/
GET    /api/telegram-bot/verified-cards/statistics/
```

## Management команды

```bash
# Запустить бота
python manage.py run_telegram_bot

# Создать верификации
python manage.py create_verified_cards [--series N] [--generate-qr] [--overwrite]

# Генерировать QR-коды
python manage.py generate_qr_codes [--card-id N] [--with-labels] [--output-dir PATH]
```

## Тесты

```bash
python manage.py test telegram_bot
```

## Документация

Полная документация в корне проекта:
- `TELEGRAM_BOT_README.md` - Подробная документация
- `QUICK_START_TELEGRAM_BOT.md` - Быстрый старт
- `TELEGRAM_BOT_EXAMPLES.md` - Примеры использования
- `TELEGRAM_BOT_CHEATSHEET.md` - Шпаргалка

