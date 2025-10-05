from rest_framework import serializers
from .models import Series, Card, Tag, CardTag


class SeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Series
        fields = ['id', 'number', 'title']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class CardSerializer(serializers.ModelSerializer):
    series_title = serializers.CharField(source='series.title', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Card
        fields = [
            'id', 'title', 'number', 'rarity', 'series', 'series_title',
            'base_price_rub', 'notes', 'tags'
        ]


class CardDetailSerializer(CardSerializer):
    series = SeriesSerializer(read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        instance = super().update(instance, validated_data)
        
        if tag_ids is not None:
            instance.tags.clear()
            for tag_id in tag_ids:
                tag = Tag.objects.get(id=tag_id)
                CardTag.objects.get_or_create(card=instance, tag=tag)
        
        return instance
    
    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        instance = super().create(validated_data)
        
        if tag_ids:
            for tag_id in tag_ids:
                tag = Tag.objects.get(id=tag_id)
                CardTag.objects.get_or_create(card=instance, tag=tag)
        
        return instance
