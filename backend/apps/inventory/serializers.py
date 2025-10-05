from rest_framework import serializers
from .models import InventoryItem, CardImage
from apps.cards.serializers import CardSerializer


class CardImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardImage
        fields = ['id', 'image', 'created_at']


class InventoryItemSerializer(serializers.ModelSerializer):
    card = CardSerializer(read_only=True)
    card_id = serializers.IntegerField(write_only=True)
    images = CardImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'card', 'card_id', 'has_card', 'quantity', 'condition',
            'user_rating', 'note', 'images'
        ]


class InventoryItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = [
            'has_card', 'quantity', 'condition', 'user_rating', 'note'
        ]


class CardImageCreateSerializer(serializers.ModelSerializer):
    inventory_item_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CardImage
        fields = ['id', 'image', 'inventory_item_id']
