# 📚 Примеры использования Telegram бота

## Сценарии использования

### 1. 🏪 Для магазина коллекционных карт

**Задача:** Защитить карты от подделок и дать покупателям возможность проверять подлинность.

**Решение:**
```bash
# 1. Создайте верификации для всех карт в инвентаре
python manage.py create_verified_cards --generate-qr

# 2. Распечатайте красивые метки
python manage.py generate_qr_codes --with-labels

# 3. Наклейте метки на карты или упаковку

# 4. Запустите бота
./run_telegram_bot.sh
```

**Результат:** Покупатели могут сканировать QR-код и мгновенно убедиться в подлинности карты.

---

### 2. 🎮 Для турниров и соревнований

**Задача:** Быстрая проверка карт участников на турнире.

**Решение:**
```bash
# Организаторы сканируют QR-коды карт участников
# Бот показывает:
# - Подлинность карты
# - Характеристики
# - Историю проверок
```

**Преимущества:**
- Быстрая проверка
- Защита от фальсификаций
- Прозрачность для всех участников

---

### 3. 📦 Для коллекционеров

**Задача:** Управление личной коллекцией.

**API запрос для получения всех ваших карт:**
```bash
curl -X GET "http://localhost:8000/api/telegram-bot/verified-cards/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Ответ:**
```json
{
  "count": 52,
  "results": [
    {
      "id": 1,
      "card": {
        "title": "Spider-Man",
        "number": 1,
        "series": "Series 1",
        "rarity": "Ультра карта"
      },
      "verification_code": "abc123",
      "verification_count": 5,
      "is_active": true
    }
  ]
}
```

---

### 4. 💰 Для торговых площадок

**Задача:** Интеграция проверки подлинности в онлайн-магазин.

**Пример интеграции:**
```javascript
// Frontend код для проверки карты
async function verifyCard(verificationCode) {
  const response = await fetch(
    `https://your-api.com/api/telegram-bot/verified-cards/verify/?code=${verificationCode}`
  );
  
  const data = await response.json();
  
  if (data.verified) {
    showSuccess(`✅ Карта подлинная: ${data.card.card.title}`);
  } else {
    showError('❌ Карта не найдена или поддельная');
  }
}
```

---

### 5. 🎁 Для дропов и лимитированных выпусков

**Задача:** Выпустить ограниченную серию карт с проверкой подлинности.

```bash
# Создать верификации только для серии 3
python manage.py create_verified_cards --series 3 --generate-qr

# Результат: QR-коды только для карт серии 3
```

---

## Примеры API запросов

### Создать верифицированную карту

```bash
curl -X POST http://localhost:8000/api/telegram-bot/verified-cards/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "card_id": 5,
    "owner_info": "Limited Edition - Owner: John Doe",
    "notes": "Mint condition, never played"
  }'
```

### Массовое создание

```bash
curl -X POST http://localhost:8000/api/telegram-bot/verified-cards/bulk_create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "card_ids": [1, 2, 3, 4, 5],
    "owner_info": "Store inventory",
    "notes": "New arrival - October 2025"
  }'
```

### Проверить карту (публичный endpoint)

```bash
curl -X GET "http://localhost:8000/api/telegram-bot/verified-cards/verify/?code=abc123"
```

### Получить статистику

```bash
curl -X GET http://localhost:8000/api/telegram-bot/verified-cards/statistics/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Ответ:**
```json
{
  "total_cards": 150,
  "active_cards": 148,
  "inactive_cards": 2,
  "total_verifications": 1234,
  "average_verifications": 8.23
}
```

### Деактивировать карту (при продаже)

```bash
curl -X POST http://localhost:8000/api/telegram-bot/verified-cards/5/deactivate/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Скачать QR-код

```bash
curl -X GET http://localhost:8000/api/telegram-bot/verified-cards/5/download_qr/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output card_5_qr.png
```

---

## Примеры использования management команд

### Создание верифицированных карт

```bash
# Все карты
python manage.py create_verified_cards

# С генерацией QR-кодов
python manage.py create_verified_cards --generate-qr

# Только серия 2
python manage.py create_verified_cards --series 2

# Перезаписать существующие
python manage.py create_verified_cards --overwrite

# Комбинация
python manage.py create_verified_cards --series 3 --generate-qr --overwrite
```

### Генерация QR-кодов

```bash
# Все карты
python manage.py generate_qr_codes

# С метками для печати
python manage.py generate_qr_codes --with-labels

# Только одна карта
python manage.py generate_qr_codes --card-id 5

# В конкретную папку
python manage.py generate_qr_codes --output-dir /path/to/output

# Комбинация
python manage.py generate_qr_codes --card-id 10 --with-labels --output-dir ./my_qr_codes
```

---

## Интеграция с Frontend

### React компонент для проверки

```typescript
import { useState } from 'react';
import { apiClient } from './api/client';

function CardVerification({ qrCode }: { qrCode: string }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const verifyCard = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get(
        `/telegram-bot/verified-cards/verify/?code=${qrCode}`
      );
      setResult(response.data);
    } catch (error) {
      setResult({ verified: false, error: 'Ошибка проверки' });
    }
    setLoading(false);
  };

  return (
    <div>
      <button onClick={verifyCard} disabled={loading}>
        {loading ? 'Проверка...' : 'Проверить подлинность'}
      </button>
      
      {result && (
        <div className={result.verified ? 'success' : 'error'}>
          {result.verified ? (
            <>
              <h3>✅ Карта подлинная!</h3>
              <p>Название: {result.card.card.title}</p>
              <p>Номер: #{result.card.card.number}</p>
              <p>Серия: {result.card.card.series.title}</p>
            </>
          ) : (
            <h3>❌ Карта не найдена</h3>
          )}
        </div>
      )}
    </div>
  );
}
```

### Отображение QR-кода в приложении

```typescript
function CardQRCode({ cardId }: { cardId: number }) {
  const qrCodeUrl = `https://your-api.com/api/telegram-bot/verified-cards/${cardId}/qr_code/`;
  
  return (
    <div className="qr-code-container">
      <h4>Проверить подлинность:</h4>
      <img src={qrCodeUrl} alt="QR Code" />
      <p>Отсканируйте QR-код для проверки</p>
    </div>
  );
}
```

---

## Автоматизация с помощью скриптов

### Python скрипт для массовой обработки

```python
#!/usr/bin/env python
"""
Скрипт для автоматической обработки новых карт
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.cards.models import Card
from telegram_bot.models import VerifiedCard
from telegram_bot.utils import create_card_qr_code, get_qr_codes_directory
from django.conf import settings

def process_new_cards():
    """Обрабатывает карты без верификации"""
    # Находим карты без верификации
    all_cards = Card.objects.all()
    verified_card_ids = VerifiedCard.objects.values_list('card_id', flat=True)
    new_cards = all_cards.exclude(id__in=verified_card_ids)
    
    print(f"Найдено новых карт: {new_cards.count()}")
    
    bot_username = settings.TELEGRAM_BOT_USERNAME
    qr_dir = get_qr_codes_directory()
    
    for card in new_cards:
        # Создаём верификацию
        verified_card = VerifiedCard.objects.create(
            card=card,
            notes=f"Автоматически создано для {card.series.title}"
        )
        
        # Генерируем QR-код
        qr_filename = f'card_{card.series.number}_{card.number}.png'
        qr_path = os.path.join(qr_dir, qr_filename)
        create_card_qr_code(verified_card, bot_username, save_path=qr_path)
        
        print(f"✅ Обработана: {card.title} #{card.number}")

if __name__ == '__main__':
    process_new_cards()
```

---

## Webhook режим (для production)

### Настройка webhook

```python
# telegram_bot/webhook.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from telegram.ext import Application
import json

@csrf_exempt
async def telegram_webhook(request):
    """Обработчик webhook от Telegram"""
    if request.method == 'POST':
        update = Update.de_json(json.loads(request.body), bot)
        await application.process_update(update)
        return JsonResponse({'ok': True})
    
    return JsonResponse({'error': 'Invalid method'}, status=405)
```

### Установка webhook

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://yourdomain.com/api/telegram-bot/webhook/"}'
```

---

## Мониторинг и аналитика

### Отслеживание популярных карт

```python
# Получить топ-10 самых проверяемых карт
from telegram_bot.models import VerifiedCard

top_cards = VerifiedCard.objects.order_by('-verification_count')[:10]

for vc in top_cards:
    print(f"{vc.card.title}: {vc.verification_count} проверок")
```

### Экспорт статистики

```python
import csv
from telegram_bot.models import VerificationLog

with open('verification_stats.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Card', 'User', 'Date', 'IP'])
    
    for log in VerificationLog.objects.all():
        writer.writerow([
            log.verified_card.card.title,
            log.telegram_username,
            log.checked_at,
            log.ip_address
        ])
```

---

## Полезные советы

### 1. Безопасность QR-кодов
- Не публикуйте QR-коды в открытом доступе до продажи карт
- Деактивируйте карты при возврате/обмене
- Регулярно проверяйте логи на подозрительную активность

### 2. Оптимизация
- Генерируйте QR-коды пачками, а не по одному
- Кэшируйте часто запрашиваемые QR-коды
- Используйте CDN для раздачи QR-кодов

### 3. UX улучшения
- Добавьте логотип на QR-коды (см. `utils.py`)
- Создавайте красивые метки с информацией о карте
- Добавьте инструкции по сканированию на упаковку

---

Нужны ещё примеры? Смотрите:
- `TELEGRAM_BOT_README.md` - подробная документация
- `QUICK_START_TELEGRAM_BOT.md` - быстрый старт
- `telegram_bot/tests.py` - примеры тестов

