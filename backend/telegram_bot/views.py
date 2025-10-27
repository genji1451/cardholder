"""
Views для API Telegram бота
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from telegram_bot.models import VerifiedCard, VerificationLog
from telegram_bot.serializers import (
    VerifiedCardSerializer,
    VerifiedCardCreateSerializer,
    VerificationLogSerializer,
    BulkVerifiedCardCreateSerializer
)
from telegram_bot.utils import create_card_qr_code, generate_printable_card_label
import io


class VerifiedCardViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления верифицированными картами
    
    list: Получить список всех верифицированных карт
    retrieve: Получить информацию о конкретной верифицированной карте
    create: Создать новую верифицированную карту
    update: Обновить верифицированную карту
    destroy: Удалить верифицированную карту
    """
    
    queryset = VerifiedCard.objects.select_related(
        'card',
        'card__series'
    ).all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == 'create':
            return VerifiedCardCreateSerializer
        elif self.action == 'bulk_create':
            return BulkVerifiedCardCreateSerializer
        return VerifiedCardSerializer
    
    def get_permissions(self):
        """Разрешения для разных действий"""
        if self.action in ['verify', 'qr_code', 'download_qr']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Массовое создание верифицированных карт
        
        POST /api/telegram-bot/verified-cards/bulk_create/
        {
            "card_ids": [1, 2, 3],
            "owner_info": "Optional owner info",
            "notes": "Optional notes"
        }
        """
        serializer = BulkVerifiedCardCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        verified_cards = serializer.save()
        
        # Возвращаем созданные карты
        result_serializer = VerifiedCardSerializer(
            verified_cards,
            many=True,
            context={'request': request}
        )
        
        return Response(
            {
                'count': len(verified_cards),
                'verified_cards': result_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Активировать карту"""
        verified_card = self.get_object()
        verified_card.activate()
        serializer = self.get_serializer(verified_card)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Деактивировать карту"""
        verified_card = self.get_object()
        verified_card.deactivate()
        serializer = self.get_serializer(verified_card)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def verify(self, request):
        """
        Проверить карту по коду верификации
        
        GET /api/telegram-bot/verified-cards/verify/?code=VERIFICATION_CODE
        """
        verification_code = request.query_params.get('code')
        
        if not verification_code:
            return Response(
                {'error': 'Код верификации не указан'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            verified_card = VerifiedCard.objects.select_related(
                'card',
                'card__series'
            ).get(
                verification_code=verification_code,
                is_active=True
            )
            
            # Увеличиваем счётчик проверок
            verified_card.verification_count += 1
            verified_card.save()
            
            serializer = self.get_serializer(verified_card)
            return Response({
                'verified': True,
                'card': serializer.data
            })
            
        except VerifiedCard.DoesNotExist:
            return Response(
                {
                    'verified': False,
                    'error': 'Карта не найдена или неактивна'
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def qr_code(self, request, pk=None):
        """
        Получить QR-код для карты
        
        GET /api/telegram-bot/verified-cards/{id}/qr_code/
        """
        verified_card = self.get_object()
        bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'your_bot')
        
        # Генерируем QR-код
        qr_buffer = create_card_qr_code(verified_card, bot_username)
        
        return HttpResponse(qr_buffer.getvalue(), content_type='image/png')
    
    @action(detail=True, methods=['get'])
    def download_qr(self, request, pk=None):
        """
        Скачать QR-код для карты
        
        GET /api/telegram-bot/verified-cards/{id}/download_qr/
        """
        verified_card = self.get_object()
        bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'your_bot')
        
        # Генерируем QR-код
        qr_buffer = create_card_qr_code(verified_card, bot_username)
        
        filename = f"card_{verified_card.card.number}_qr.png"
        response = HttpResponse(qr_buffer.getvalue(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    @action(detail=True, methods=['get'])
    def printable_label(self, request, pk=None):
        """
        Получить метку для печати (QR-код + информация о карте)
        
        GET /api/telegram-bot/verified-cards/{id}/printable_label/
        """
        verified_card = self.get_object()
        bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'your_bot')
        
        # Генерируем метку
        label_buffer = generate_printable_card_label(verified_card, bot_username)
        
        filename = f"card_{verified_card.card.number}_label.png"
        response = HttpResponse(label_buffer.getvalue(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Получить статистику по верифицированным картам
        
        GET /api/telegram-bot/verified-cards/statistics/
        """
        total_cards = self.queryset.count()
        active_cards = self.queryset.filter(is_active=True).count()
        inactive_cards = total_cards - active_cards
        total_verifications = sum(
            self.queryset.values_list('verification_count', flat=True)
        )
        
        return Response({
            'total_cards': total_cards,
            'active_cards': active_cards,
            'inactive_cards': inactive_cards,
            'total_verifications': total_verifications,
            'average_verifications': (
                total_verifications / total_cards if total_cards > 0 else 0
            )
        })


class VerificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра логов верификации (только чтение)
    
    list: Получить список всех логов
    retrieve: Получить информацию о конкретном логе
    """
    
    queryset = VerificationLog.objects.select_related(
        'verified_card',
        'verified_card__card',
        'verified_card__card__series'
    ).all()
    serializer_class = VerificationLogSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Получить последние логи верификации
        
        GET /api/telegram-bot/verification-logs/recent/?limit=10
        """
        limit = int(request.query_params.get('limit', 10))
        logs = self.queryset.order_by('-checked_at')[:limit]
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_card(self, request):
        """
        Получить логи для конкретной верифицированной карты
        
        GET /api/telegram-bot/verification-logs/by_card/?card_id=1
        """
        card_id = request.query_params.get('card_id')
        
        if not card_id:
            return Response(
                {'error': 'card_id не указан'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logs = self.queryset.filter(verified_card_id=card_id)
        serializer = self.get_serializer(logs, many=True)
        
        return Response({
            'count': logs.count(),
            'logs': serializer.data
        })

