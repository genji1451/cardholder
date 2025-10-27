"""
Serializers для API Telegram бота
"""

from rest_framework import serializers
from telegram_bot.models import VerifiedCard, VerificationLog


class VerifiedCardSerializer(serializers.ModelSerializer):
    """Serializer для верифицированных карт"""
    
    card = serializers.SerializerMethodField()
    card_id = serializers.IntegerField(write_only=True, source='card.id', required=False)
    bot_link = serializers.SerializerMethodField()
    qr_code_url = serializers.SerializerMethodField()
    
    class Meta:
        model = VerifiedCard
        fields = [
            'id',
            'card',
            'card_id',
            'verification_code',
            'is_active',
            'verification_count',
            'owner_info',
            'notes',
            'created_at',
            'updated_at',
            'bot_link',
            'qr_code_url'
        ]
        read_only_fields = [
            'verification_code',
            'verification_count',
            'created_at',
            'updated_at'
        ]
    
    def get_card(self, obj):
        """Получить информацию о карте"""
        from apps.cards.serializers import CardSerializer
        return CardSerializer(obj.card).data
    
    def get_bot_link(self, obj):
        """Получить ссылку на бота"""
        from django.conf import settings
        bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'your_bot')
        return obj.get_bot_link(bot_username)
    
    def get_qr_code_url(self, obj):
        """URL для получения QR-кода"""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/telegram-bot/qr-code/{obj.id}/')
        return f'/api/telegram-bot/qr-code/{obj.id}/'


class VerifiedCardCreateSerializer(serializers.ModelSerializer):
    """Serializer для создания верифицированной карты"""
    
    card_id = serializers.IntegerField(source='card.id')
    
    class Meta:
        model = VerifiedCard
        fields = [
            'card_id',
            'owner_info',
            'notes',
            'is_active'
        ]
    
    def create(self, validated_data):
        """Создание верифицированной карты"""
        from apps.cards.models import Card
        card_id = validated_data.pop('card')['id']
        card = Card.objects.get(id=card_id)
        return VerifiedCard.objects.create(card=card, **validated_data)


class VerificationLogSerializer(serializers.ModelSerializer):
    """Serializer для логов верификации"""
    
    verified_card = VerifiedCardSerializer(read_only=True)
    card_info = serializers.SerializerMethodField()
    
    class Meta:
        model = VerificationLog
        fields = [
            'id',
            'verified_card',
            'card_info',
            'telegram_user_id',
            'telegram_username',
            'checked_at',
            'ip_address'
        ]
    
    def get_card_info(self, obj):
        """Краткая информация о карте"""
        card = obj.verified_card.card
        return {
            'id': card.id,
            'title': card.title,
            'number': card.number,
            'series': card.series.title
        }


class BulkVerifiedCardCreateSerializer(serializers.Serializer):
    """Serializer для массового создания верифицированных карт"""
    
    card_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text='Список ID карт для создания верификации'
    )
    owner_info = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Общая информация о владельце для всех карт'
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Общие примечания для всех карт'
    )
    
    def validate_card_ids(self, value):
        """Проверяем, что все карты существуют"""
        from apps.cards.models import Card
        
        existing_cards = Card.objects.filter(id__in=value)
        existing_ids = set(existing_cards.values_list('id', flat=True))
        requested_ids = set(value)
        
        missing_ids = requested_ids - existing_ids
        if missing_ids:
            raise serializers.ValidationError(
                f"Карты с ID {missing_ids} не найдены"
            )
        
        return value
    
    def create(self, validated_data):
        """Создаём верифицированные карты для всех указанных карт"""
        from apps.cards.models import Card
        
        card_ids = validated_data['card_ids']
        owner_info = validated_data.get('owner_info', '')
        notes = validated_data.get('notes', '')
        
        verified_cards = []
        for card_id in card_ids:
            card = Card.objects.get(id=card_id)
            verified_card = VerifiedCard.objects.create(
                card=card,
                owner_info=owner_info,
                notes=notes
            )
            verified_cards.append(verified_card)
        
        return verified_cards

