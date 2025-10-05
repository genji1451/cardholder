from django.db import models
from django.conf import settings

from apps.cards.models import Card


class InventoryItem(models.Model):
    CONDITION_CHOICES = [
        ("M", "Mint"),
        ("NM", "Near Mint"),
        ("SP", "Slightly Played"),
        ("MP", "Moderately Played"),
        ("HP", "Heavily Played"),
        ("DM", "Damaged"),
        ("NO", "Нет в коллекции"),
    ]

    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="inventory_items")
    has_card = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=0)
    condition = models.CharField(max_length=2, choices=CONDITION_CHOICES, default="NO")
    user_rating = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    note = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inventory")

    class Meta:
        unique_together = ("card", "owner")

    def __str__(self):
        return f"{self.card} x{self.quantity} ({self.condition})"


def card_image_upload_to(instance, filename):
    return f"cards/{instance.inventory_item.card.series.number}/{instance.inventory_item.card.number}/{filename}"


class CardImage(models.Model):
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=card_image_upload_to)
    created_at = models.DateTimeField(auto_now_add=True)

# Create your models here.
