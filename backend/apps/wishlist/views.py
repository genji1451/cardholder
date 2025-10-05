from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import WishlistItem
from .serializers import WishlistItemSerializer


class WishlistItemViewSet(viewsets.ModelViewSet):
    queryset = WishlistItem.objects.all()
    serializer_class = WishlistItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['priority', 'card__rarity', 'card__series']
    search_fields = ['card__title', 'note']
    ordering_fields = ['priority', 'target_price_rub', 'created_at']
    ordering = ['-priority', 'created_at']

    def get_queryset(self):
        # For testing, return all items without user filtering
        return WishlistItem.objects.select_related(
            'card__series'
        )

    def perform_create(self, serializer):
        # Для тестирования используем тестового пользователя
        from django.contrib.auth.models import User
        test_user, _ = User.objects.get_or_create(username='test_user')
        serializer.save(owner=test_user)