from rest_framework import serializers
from .models import WishlistItem
from apps.cards.serializers import CardSerializer


class WishlistItemSerializer(serializers.ModelSerializer):
    card = CardSerializer(read_only=True)
    card_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = WishlistItem
        fields = [
            'id', 'card', 'card_id', 'priority', 'target_price_rub',
            'note', 'created_at'
        ]
        read_only_fields = ['created_at']
