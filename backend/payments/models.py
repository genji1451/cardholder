from django.db import models
from django.contrib.auth.models import User
import uuid
import hashlib
import hmac
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class Order(models.Model):
    """Модель заказа"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('cancelled', 'Отменен'),
        ('refunded', 'Возвращен'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    telegram_username = models.CharField(max_length=100, blank=True, verbose_name='Ник в Telegram')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Информация о доставке
    delivery_address = models.TextField(blank=True)
    delivery_method = models.CharField(max_length=100, blank=True)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заказ {self.id} - {self.total_amount}₽"


class OrderItem(models.Model):
    """Товары в заказе"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()
    product_title = models.CharField(max_length=200)
    product_description = models.TextField(blank=True)
    product_image = models.URLField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    # Опции товара
    has_case = models.BooleanField(default=False)
    film_type = models.CharField(max_length=20, choices=[
        ('none', 'Без пленки'),
        ('holographic', 'Голографическая'),
        ('metallic', 'Металлическая'),
    ], default='none')
    
    def __str__(self):
        return f"{self.product_title} x{self.quantity}"


class Payment(models.Model):
    """Модель платежа"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('success', 'Успешно'),
        ('failed', 'Неуспешно'),
        ('cancelled', 'Отменен'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    robokassa_invoice_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='RUB')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Данные от Robokassa
    robokassa_response = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"Платеж {self.robokassa_invoice_id} - {self.amount}₽"
    
    def generate_signature(self):
        """Генерация подписи для Robokassa"""
        try:
            signature_string = f"{settings.ROBOKASSA_LOGIN}:{self.amount}:{self.order.id}:{settings.ROBOKASSA_PASSWORD1}"
            return hashlib.md5(signature_string.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error generating signature: {str(e)}")
            raise
    
    def verify_signature(self, signature):
        """Проверка подписи от Robokassa"""
        expected_signature = self.generate_signature()
        return hmac.compare_digest(signature, expected_signature)