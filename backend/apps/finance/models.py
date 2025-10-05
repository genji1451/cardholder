from django.db import models
from apps.cards.models import Card


class Trade(models.Model):
    TRADE_TYPE = [
        ("buy", "Purchase"),
        ("sell", "Sale"),
    ]

    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="trades")
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPE)
    quantity = models.PositiveIntegerField(default=1)
    price_rub = models.DecimalField(max_digits=10, decimal_places=2)
    fees_rub = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField()
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.trade_type} {self.card} x{self.quantity} @ {self.price_rub}₽"


class PriceRecord(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="price_records")
    source = models.CharField(max_length=50, default="sheets")
    price_rub = models.DecimalField(max_digits=10, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)

# Create your models here.
