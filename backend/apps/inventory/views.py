from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import InventoryItem, CardImage
from .serializers import (
    InventoryItemSerializer, InventoryItemUpdateSerializer,
    CardImageSerializer, CardImageCreateSerializer
)


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['condition', 'has_card']
    search_fields = ['card__title', 'card__number', 'note']
    ordering_fields = ['card__number', 'card__title', 'user_rating']
    ordering = ['card__series__number', 'card__number']

    def get_queryset(self):
        # For testing, return all items without user filtering
        return InventoryItem.objects.select_related(
            'card__series'
        ).prefetch_related(
            'images'
        )

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return InventoryItemUpdateSerializer
        return InventoryItemSerializer

    def perform_create(self, serializer):
        # Для тестирования используем тестового пользователя
        from django.contrib.auth.models import User
        test_user, _ = User.objects.get_or_create(username='test_user')
        
        # Проверяем, есть ли уже такая карточка в инвентаре
        card_id = serializer.validated_data.get('card_id')
        existing_item = InventoryItem.objects.filter(owner=test_user, card_id=card_id).first()
        
        if existing_item:
            # Если карточка уже есть, обновляем её
            existing_item.has_card = True
            existing_item.quantity = serializer.validated_data.get('quantity', 1)
            existing_item.condition = serializer.validated_data.get('condition', 'NM')
            existing_item.user_rating = serializer.validated_data.get('user_rating', 8.0)
            existing_item.save()
            serializer.instance = existing_item
        else:
            # Если карточки нет, создаём новую
            serializer.save(owner=test_user)

    @action(detail=False, methods=['get'])
    def owned(self, request):
        """Получить только карточки, которые есть в коллекции"""
        queryset = self.get_queryset().filter(has_card=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def missing(self, request):
        """Получить карточки, которых нет в коллекции"""
        queryset = self.get_queryset().filter(has_card=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CardImageViewSet(viewsets.ModelViewSet):
    queryset = CardImage.objects.all()
    serializer_class = CardImageSerializer

    def get_queryset(self):
        # For testing, return all images without user filtering
        return CardImage.objects.select_related('inventory_item__card')

    def get_serializer_class(self):
        if self.action in ['create']:
            return CardImageCreateSerializer
        return CardImageSerializer

    def perform_create(self, serializer):
        inventory_item_id = serializer.validated_data.pop('inventory_item_id')
        inventory_item = InventoryItem.objects.get(
            id=inventory_item_id,
            owner=self.request.user
        )
        serializer.save(inventory_item=inventory_item)