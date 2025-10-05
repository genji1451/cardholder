from rest_framework import serializers
from .models import Trade, PriceRecord
from apps.cards.serializers import CardSerializer


class TradeSerializer(serializers.ModelSerializer):
    card = CardSerializer(read_only=True)
    card_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Trade
        fields = [
            'id', 'card', 'card_id', 'trade_type', 'quantity',
            'price_rub', 'fees_rub', 'date', 'note'
        ]


class PriceRecordSerializer(serializers.ModelSerializer):
    card = CardSerializer(read_only=True)
    card_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = PriceRecord
        fields = ['id', 'card', 'card_id', 'source', 'price_rub', 'recorded_at']
        read_only_fields = ['recorded_at']
