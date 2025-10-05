from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg
from .models import Trade, PriceRecord
from .serializers import TradeSerializer, PriceRecordSerializer


class TradeViewSet(viewsets.ModelViewSet):
    queryset = Trade.objects.select_related('card__series')
    serializer_class = TradeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['trade_type', 'card__rarity', 'card__series']
    search_fields = ['card__title', 'note']
    ordering_fields = ['date', 'price_rub']
    ordering = ['-date']


class PriceRecordViewSet(viewsets.ModelViewSet):
    queryset = PriceRecord.objects.select_related('card__series')
    serializer_class = PriceRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['source', 'card__rarity', 'card__series']
    search_fields = ['card__title']
    ordering_fields = ['recorded_at', 'price_rub']
    ordering = ['-recorded_at']