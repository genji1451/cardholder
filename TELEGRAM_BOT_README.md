# Telegram Bot для проверки подлинности карт

## 📋 Описание

Этот Telegram бот позволяет проверять подлинность коллекционных карточек через QR-коды. Каждая карта имеет уникальный QR-код, который содержит ссылку на бота. При сканировании QR-кода пользователь получает:

- ✅ Подтверждение подлинности карты
- 🖼️ Фотографию карты
- 📊 Информацию о карте (название, серия, редкость, цена)
- 📈 Статистику проверок

## 🏗️ Структура проекта

```
backend/telegram_bot/
├── __init__.py                 # Инициализация приложения
├── apps.py                     # Конфигурация Django приложения
├── models.py                   # Модели базы данных
├── admin.py                    # Административная панель
├── serializers.py              # API сериализаторы
├── views.py                    # API views
├── urls.py                     # URL маршруты
├── bot.py                      # Основной код Telegram бота
├── utils.py                    # Утилиты для генерации QR-кодов
├── migrations/                 # Миграции базы данных
│   └── __init__.py
└── management/                 # Management команды
    └── commands/
        ├── run_telegram_bot.py         # Запуск бота
        ├── create_verified_cards.py    # Создание верифицированных карт
        └── generate_qr_codes.py        # Генерация QR-кодов
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте или обновите файл `.env` в директории `backend/`:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_BOT_USERNAME=your_bot_username
```

### 3. Создание и настройка бота в Telegram

1. Откройте [@BotFather](https://t.me/botfather) в Telegram
2. Создайте нового бота командой `/newbot`
3. Следуйте инструкциям и получите токен бота
4. Скопируйте токен в `.env` файл
5. Установите описание бота командой `/setdescription`
6. Установите команды бота командой `/setcommands`:

```
start - Начать работу с ботом
help - Помощь по использованию
info - Информация о системе проверки
```

### 4. Применение миграций

```bash
python manage.py makemigrations telegram_bot
python manage.py migrate
```

### 5. Создание верифицированных карт

Создайте верифицированные карты для всех существующих карт в базе данных:

```bash
# Создать верификации для всех карт
python manage.py create_verified_cards

# Создать верификации и сгенерировать QR-коды
python manage.py create_verified_cards --generate-qr

# Создать только для определённой серии
python manage.py create_verified_cards --series 1 --generate-qr
```

### 6. Генерация QR-кодов

```bash
# Сгенерировать QR-коды для всех верифицированных карт
python manage.py generate_qr_codes

# Сгенерировать QR-коды с метками для печати
python manage.py generate_qr_codes --with-labels

# Указать директорию для сохранения
python manage.py generate_qr_codes --output-dir /path/to/output
```

### 7. Запуск бота

**Вариант 1: Через скрипт**
```bash
./run_telegram_bot.sh
```

**Вариант 2: Через management команду**
```bash
python manage.py run_telegram_bot
```

**Вариант 3: Напрямую**
```bash
python telegram_bot/bot.py
```

## 📱 Использование

### Для администратора

1. **Создание верифицированной карты через админку:**
   - Откройте Django admin панель
   - Перейдите в раздел "Верифицированные карты"
   - Нажмите "Добавить верифицированную карту"
   - Выберите карту, добавьте информацию
   - Скачайте QR-код через админку

2. **Массовое создание через команду:**
   ```bash
   python manage.py create_verified_cards --generate-qr
   ```

3. **Печать меток на карты:**
   - Сгенерируйте метки: `python manage.py generate_qr_codes --with-labels`
   - Метки будут сохранены в `media/qr_codes/labels/`
   - Распечатайте и наклейте на карты

### Для пользователей

1. **Проверка карты через QR-код:**
   - Отсканируйте QR-код на карте камерой телефона
   - Перейдите по ссылке
   - Telegram автоматически откроет бота
   - Получите информацию о карте

2. **Команды бота:**
   - `/start` - Начать работу
   - `/help` - Справка
   - `/info` - Информация о системе

## 🔌 API Endpoints

Бот предоставляет REST API для интеграции:

### Верифицированные карты

```
GET    /api/telegram-bot/verified-cards/              # Список всех верифицированных карт
POST   /api/telegram-bot/verified-cards/              # Создать новую верифицированную карту
GET    /api/telegram-bot/verified-cards/{id}/         # Получить конкретную карту
PUT    /api/telegram-bot/verified-cards/{id}/         # Обновить карту
DELETE /api/telegram-bot/verified-cards/{id}/         # Удалить карту

POST   /api/telegram-bot/verified-cards/bulk_create/  # Массовое создание
GET    /api/telegram-bot/verified-cards/verify/?code=XXX  # Проверить карту по коду
POST   /api/telegram-bot/verified-cards/{id}/activate/    # Активировать карту
POST   /api/telegram-bot/verified-cards/{id}/deactivate/  # Деактивировать карту
GET    /api/telegram-bot/verified-cards/{id}/qr_code/     # Получить QR-код
GET    /api/telegram-bot/verified-cards/{id}/download_qr/ # Скачать QR-код
GET    /api/telegram-bot/verified-cards/{id}/printable_label/  # Получить метку для печати
GET    /api/telegram-bot/verified-cards/statistics/  # Статистика
```

### Логи верификации

```
GET /api/telegram-bot/verification-logs/           # Список логов
GET /api/telegram-bot/verification-logs/{id}/      # Конкретный лог
GET /api/telegram-bot/verification-logs/recent/    # Последние логи
GET /api/telegram-bot/verification-logs/by_card/?card_id=X  # Логи по карте
```

### Примеры использования API

**Проверить карту по коду:**
```bash
curl -X GET "http://localhost:8000/api/telegram-bot/verified-cards/verify/?code=abc123"
```

**Создать верифицированную карту:**
```bash
curl -X POST http://localhost:8000/api/telegram-bot/verified-cards/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "card_id": 1,
    "owner_info": "John Doe",
    "notes": "Mint condition"
  }'
```

**Скачать QR-код:**
```bash
curl -X GET http://localhost:8000/api/telegram-bot/verified-cards/1/download_qr/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output qr_code.png
```

## 🗄️ Модели данных

### VerifiedCard

Хранит информацию о верифицированных картах.

**Поля:**
- `card` (ForeignKey) - Связь с моделью Card
- `verification_code` (CharField) - Уникальный код для QR
- `is_active` (BooleanField) - Активна ли карта
- `verification_count` (IntegerField) - Количество проверок
- `owner_info` (TextField) - Информация о владельце
- `notes` (TextField) - Примечания
- `created_at` (DateTimeField) - Дата создания
- `updated_at` (DateTimeField) - Дата обновления

### VerificationLog

Хранит историю всех проверок карт.

**Поля:**
- `verified_card` (ForeignKey) - Проверенная карта
- `telegram_user_id` (BigIntegerField) - ID пользователя Telegram
- `telegram_username` (CharField) - Username пользователя
- `checked_at` (DateTimeField) - Время проверки
- `ip_address` (GenericIPAddressField) - IP адрес
- `user_agent` (TextField) - User agent

## 🎨 Административная панель

Django admin предоставляет удобный интерфейс для управления картами:

**Возможности:**
- 📋 Просмотр всех верифицированных карт
- ➕ Создание новых верификаций
- ✏️ Редактирование информации
- ❌ Деактивация карт
- 📱 Просмотр и скачивание QR-кодов
- 🔗 Копирование ссылок на бота
- 📊 Просмотр логов проверок

**Массовые действия:**
- Активация выбранных карт
- Деактивация выбранных карт
- Генерация QR-кодов

## 🔐 Безопасность

### Защита от подделок

1. **Уникальные коды:** Каждая карта имеет UUID-based код верификации
2. **Активация/деактивация:** Карты можно деактивировать при утере
3. **Логирование:** Все проверки записываются в лог
4. **Статистика:** Отслеживание количества проверок

### Приватность

- Бот не собирает личные данные без согласия
- Логи содержат только Telegram ID и username
- IP адреса хранятся для безопасности

## 🛠️ Разработка и тестирование

### Тестирование бота локально

1. Запустите бота: `python manage.py run_telegram_bot`
2. Создайте тестовую карту через admin панель
3. Скачайте QR-код
4. Отсканируйте QR-код телефоном
5. Проверьте работу бота

### Отладка

Включите DEBUG режим в `settings.py`:
```python
DEBUG = True
```

Логи бота выводятся в консоль.

## 📊 Мониторинг и статистика

### Через API

```bash
# Получить общую статистику
curl -X GET http://localhost:8000/api/telegram-bot/verified-cards/statistics/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Результат:**
```json
{
  "total_cards": 150,
  "active_cards": 148,
  "inactive_cards": 2,
  "total_verifications": 1234,
  "average_verifications": 8.23
}
```

### Через админку

- Просматривайте логи в разделе "Логи верификаций"
- Фильтруйте по датам, картам, пользователям
- Экспортируйте данные для анализа

## 🚨 Troubleshooting

### Бот не запускается

**Проблема:** `TELEGRAM_BOT_TOKEN не настроен`
- Проверьте файл `.env`
- Убедитесь, что токен правильный
- Проверьте, что переменная называется `TELEGRAM_BOT_TOKEN`

### QR-коды не генерируются

**Проблема:** Ошибка при создании QR-кода
- Установите pillow: `pip install Pillow`
- Установите qrcode: `pip install qrcode[pil]`
- Проверьте права на запись в `media/qr_codes/`

### Изображения карт не отображаются

**Проблема:** Бот отправляет сообщение без фото
- Проверьте наличие изображений в `frontend/public/images/spiderman/`
- Убедитесь, что путь в `utils.py` правильный
- Проверьте расширения файлов (.svg, .png, .jpg)

### API возвращает 403

**Проблема:** Отсутствует аутентификация
- Добавьте токен в header: `Authorization: Bearer YOUR_TOKEN`
- Для публичных endpoints (verify) токен не нужен

## 📝 TODO / Будущие улучшения

- [ ] Webhook режим для production
- [ ] Интеграция с платёжными системами
- [ ] Система рейтингов карт
- [ ] Торговая площадка через бота
- [ ] Уведомления о новых картах
- [ ] Интеграция с другими мессенджерами
- [ ] Мобильное приложение для сканирования

## 📞 Поддержка

Если у вас возникли вопросы или проблемы:

1. Проверьте эту документацию
2. Посмотрите логи бота
3. Проверьте admin панель
4. Создайте issue в репозитории

## 📄 Лицензия

Этот проект является частью системы управления коллекцией карт.

