# 🛍️ Руководство по полноценному магазину

## ✅ Что реализовано

### 1. **Магазин (ShopPage)**
- ✅ Каталог товаров с фильтрами
- ✅ Категории: Карточки 🎴 и Картины 🎨
- ✅ Фильтр по редкости (Обычная, Редкая, Ультра)
- ✅ Кнопка "В корзину" на каждом товаре
- ✅ Уведомления при добавлении в корзину
- ✅ Счетчик товаров в корзине (бейдж)

### 2. **Корзина (CartPage)**
#### Шаг 1: Корзина
- ✅ Просмотр всех товаров
- ✅ Изменение количества (+/-)
- ✅ Удаление товаров
- ✅ Подсчет суммы + доставка
- ✅ Сохранение в localStorage

#### Шаг 2: Доставка
- ✅ Форма с полями:
  - ФИО *
  - Телефон *
  - Email *
  - Страна *
  - Город *
  - Адрес *
  - Индекс
  - Комментарий
- ✅ Валидация обязательных полей

#### Шаг 3: Оплата
- ✅ Выбор способа оплаты:
  - 💳 Банковская карта
  - 📱 СБП
  - 🛒 OZON Pay
- ✅ Итоговая сумма заказа
- ✅ Защищенная оплата

### 3. **Навигация**
- ✅ Кнопка "🛒 Корзина" в шапке магазина
- ✅ Красный бейдж с количеством товаров
- ✅ Анимация пульсации бейджа

---

## 🚀 Как проверить

### **Магазин:**
```
https://portfolio.cards/shop
```

### **Корзина:**
```
https://portfolio.cards/cart
```

### **Процесс покупки:**
1. Перейдите в магазин
2. Нажмите "🛒 В корзину" на любом товаре
3. Увидите уведомление о добавлении
4. Нажмите "🛒 Корзина (1)" в шапке
5. Измените количество или удалите товары
6. Нажмите "Перейти к оформлению"
7. Заполните форму доставки
8. Выберите способ оплаты
9. Нажмите "Оплатить"

---

## 📝 Что нужно настроить

### 1. **Товары** (`frontend/src/pages/ShopPage.tsx`)
Массив `mockProducts` (строки 18-92):
```typescript
{
  id: 1,
  title: "Название товара",
  description: "Описание",
  price: 2500,  // Цена в рублях
  category: 'card', // 'card' или 'art'
  rarity: 'ultra', // 'common', 'rare', 'ultra'
  image: '/images/path.jpg',
  available: true, // true или false
  featured: true, // показать в Featured секции
}
```

### 2. **Telegram для связи** (`frontend/src/pages/ShopPage.tsx`)
Строка 308:
```typescript
href="https://t.me/your_username"
```
Замените `your_username` на ваш реальный Telegram.

### 3. **Обработка заказа** (`frontend/src/pages/CartPage.tsx`)
Строка 55-110 - функция `handlePayment()`:

**Сейчас:** Имитация заказа (alert + console.log)

**Для production нужно:**
```typescript
// 1. Отправить заказ на бэкенд
const response = await fetch('/api/orders', {
  method: 'POST',
  body: JSON.stringify({
    items: cart,
    delivery: deliveryForm,
    paymentMethod,
    totalPrice: finalPrice,
  })
});

// 2. Получить платежную ссылку
const { paymentUrl } = await response.json();

// 3. Редирект на оплату
window.location.href = paymentUrl;
```

---

## 💳 Интеграция платежей

### **Варианты:**

#### 1. **YooKassa (ЮKassa)** - Рекомендую для РФ
```bash
npm install @a2seven/yoo-checkout
```

**Backend (Django):**
```python
from yookassa import Configuration, Payment

Configuration.account_id = 'YOUR_SHOP_ID'
Configuration.secret_key = 'YOUR_SECRET_KEY'

payment = Payment.create({
    "amount": {
        "value": "100.00",
        "currency": "RUB"
    },
    "confirmation": {
        "type": "redirect",
        "return_url": "https://portfolio.cards/success"
    },
    "description": "Заказ №1"
})

payment_url = payment.confirmation.confirmation_url
```

**Документация:** https://yookassa.ru/developers/

#### 2. **Tinkoff Acquiring**
- https://www.tinkoff.ru/business/acquiring/

#### 3. **Stripe** (международные платежи)
- https://stripe.com/docs

---

## 📦 Backend для заказов (Django)

### Создайте модель заказа:
```python
# backend/apps/shop/models.py
from django.db import models

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('shipped', 'Отправлен'),
        ('completed', 'Завершен'),
    ]
    
    # Данные заказа
    order_number = models.CharField(max_length=50, unique=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Доставка
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100)
    comment = models.TextField(blank=True)
    
    # Оплата
    payment_method = models.CharField(max_length=20)
    payment_id = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_id = models.IntegerField()
    product_title = models.CharField(max_length=200)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
```

### API endpoint:
```python
# backend/apps/shop/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def create_order(request):
    data = request.data
    
    # 1. Создать заказ в БД
    order = Order.objects.create(
        order_number=generate_order_number(),
        total_price=data['totalPrice'],
        status='pending',
        full_name=data['delivery']['fullName'],
        phone=data['delivery']['phone'],
        email=data['delivery']['email'],
        address=data['delivery']['address'],
        city=data['delivery']['city'],
        postal_code=data['delivery']['postalCode'],
        country=data['delivery']['country'],
        comment=data['delivery']['comment'],
        payment_method=data['paymentMethod'],
    )
    
    # 2. Создать items
    for item in data['items']:
        OrderItem.objects.create(
            order=order,
            product_id=item['id'],
            product_title=item['title'],
            quantity=item['quantity'],
            price=item['price'],
        )
    
    # 3. Создать платеж через YooKassa
    payment = create_payment(order)
    
    # 4. Отправить уведомление в Telegram
    send_telegram_notification(order)
    
    return Response({
        'orderId': order.id,
        'paymentUrl': payment.confirmation.confirmation_url
    })
```

---

## 📱 Telegram уведомления

В `handlePayment()` добавьте отправку в Telegram Bot:

```typescript
// Отправить уведомление в Telegram
await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    chat_id: YOUR_CHAT_ID,
    text: `🛍️ НОВЫЙ ЗАКАЗ\n\n${orderMessage}`,
    parse_mode: 'HTML'
  })
});
```

---

## 🎨 Кастомизация

### Изменить цены доставки:
`frontend/src/pages/CartPage.tsx`, строка 34:
```typescript
const deliveryPrice = 500; // Измените здесь
```

### Изменить способы оплаты:
Добавьте или удалите методы в разделе Payment Step (строки 234-280).

### Изменить валюту:
Замените `₽` на `$` или другую валюту во всех файлах.

---

## 🔒 Безопасность

1. **НИКОГДА** не храните ключи API в frontend коде
2. Вся платежная логика должна быть на backend
3. Проверяйте webhook'и от платежных систем
4. Используйте HTTPS для всех запросов
5. Валидируйте все данные на сервере

---

## ✅ Готово к использованию!

Магазин полностью работает локально. 

**Для production:**
1. Добавьте реальные товары
2. Настройте backend API
3. Интегрируйте платежную систему
4. Настройте Telegram уведомления
5. Протестируйте весь процесс

---

## 📞 Поддержка

Если возникнут вопросы по настройке платежей или backend - спрашивайте!

