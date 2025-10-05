from django.db import models
from django.conf import settings
from apps.cards.models import Card


class WishlistItem(models.Model):
    PRIORITY = [
        (1, "Low"),
        (2, "Medium"),
        (3, "High"),
    ]

    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="wishlist_items")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist")
    priority = models.IntegerField(choices=PRIORITY, default=2)
    target_price_rub = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("card", "owner")

# Create your models here.
