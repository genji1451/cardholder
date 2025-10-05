from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, Q
from apps.cards.models import Card
from apps.inventory.models import InventoryItem
from apps.finance.models import Trade, PriceRecord


class AnalyticsOverviewView(APIView):
    def get(self, request):
        # For now, get the first user for testing
        from django.contrib.auth.models import User
        user = User.objects.first()
        
        # Общее количество карточек
        total_cards = Card.objects.count()
        
        # Карточки в коллекции
        owned_cards = InventoryItem.objects.filter(
            owner=user, has_card=True
        ).count()
        
        # Процент заполнения коллекции
        completion_percentage = (owned_cards / total_cards * 100) if total_cards > 0 else 0
        
        # Общая стоимость коллекции (по базовым ценам)
        total_value = InventoryItem.objects.filter(
            owner=user, has_card=True
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        # Последние покупки
        recent_trades = Trade.objects.filter(
            trade_type='buy'
        ).select_related('card').order_by('-date')[:5]
        
        return Response({
            'total_cards': total_cards,
            'owned_cards': owned_cards,
            'completion_percentage': round(completion_percentage, 1),
            'total_value': total_value,
            'recent_trades': [
                {
                    'card_title': trade.card.title,
                    'quantity': trade.quantity,
                    'price': float(trade.price_rub),
                    'date': trade.date
                }
                for trade in recent_trades
            ]
        })


class AnalyticsDistributionView(APIView):
    def get(self, request):
        # For now, get the first user for testing
        from django.contrib.auth.models import User
        user = User.objects.first()
        
        # Распределение по редкости
        rarity_distribution = InventoryItem.objects.filter(
            owner=user, has_card=True
        ).values('card__rarity').annotate(
            count=Count('id')
        ).order_by('card__rarity')
        
        # Распределение по сериям
        series_distribution = InventoryItem.objects.filter(
            owner=user, has_card=True
        ).values(
            'card__series__number', 'card__series__title'
        ).annotate(
            count=Count('id')
        ).order_by('card__series__number')
        
        return Response({
            'rarity': list(rarity_distribution),
            'series': list(series_distribution)
        })


class AnalyticsProgressView(APIView):
    def get(self, request):
        # For now, get the first user for testing
        from django.contrib.auth.models import User
        user = User.objects.first()
        
        # Прогресс по сериям
        series_progress = []
        for series in Card.objects.values('series__id', 'series__title', 'series__number').distinct():
            total_in_series = Card.objects.filter(series_id=series['series__id']).count()
            owned_in_series = InventoryItem.objects.filter(
                owner=user, has_card=True, card__series_id=series['series__id']
            ).count()
            
            series_progress.append({
                'series_id': series['series__id'],
                'series_title': series['series__title'],
                'series_number': series['series__number'],
                'total': total_in_series,
                'owned': owned_in_series,
                'percentage': round((owned_in_series / total_in_series * 100) if total_in_series > 0 else 0, 1)
            })
        
        return Response({'series_progress': series_progress})


class AnalyticsValueTrendView(APIView):
    def get(self, request):
        # For now, get the first user for testing
        from django.contrib.auth.models import User
        user = User.objects.first()
        
        # Тренд стоимости по месяцам
        trades = Trade.objects.filter(
            trade_type='buy'
        ).extra(
            select={'month': "DATE_TRUNC('month', date)"}
        ).values('month').annotate(
            total_spent=Sum('price_rub'),
            avg_price=Avg('price_rub')
        ).order_by('month')
        
        return Response({
            'value_trend': list(trades)
        })