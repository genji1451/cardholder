from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Series, Card, Tag
from .serializers import SeriesSerializer, CardSerializer, CardDetailSerializer, TagSerializer


class SeriesViewSet(viewsets.ModelViewSet):
    queryset = Series.objects.all()
    serializer_class = SeriesSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['number', 'title']
    ordering = ['number']


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rarity', 'series']
    search_fields = ['title', 'number']
    ordering_fields = ['number', 'title', 'base_price_rub']
    ordering = ['series__number', 'number']

    def get_queryset(self):
        """Get queryset with fallback for empty database"""
        try:
            return Card.objects.all()
        except Exception:
            # If database is not initialized, return empty queryset
            return Card.objects.none()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CardDetailSerializer
        return CardSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']