from django.db import models


class Series(models.Model):
    number = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=100, default="Series 1")

    def __str__(self):
        return f"Series {self.number}: {self.title}"


class Card(models.Model):
    RARITY_CHOICES = [
        ("o", "Обычная"),
        ("ск", "Средняя карта"),
        ("ук", "Ультра карта"),
    ]

    title = models.CharField(max_length=120)
    number = models.PositiveIntegerField()
    rarity = models.CharField(max_length=2, choices=RARITY_CHOICES)
    series = models.ForeignKey(Series, on_delete=models.PROTECT, related_name="cards")
    base_price_rub = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("series", "number")
        ordering = ["series__number", "number"]

    def __str__(self):
        return f"{self.title} #{self.number} (S{self.series.number})"


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class CardTag(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("card", "tag")

# Create your models here.
