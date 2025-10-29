from rest_framework import serializers
from .models import Order, OrderItem, Payment


class OrderItemSerializer(serializers.ModelSerializer):
    # Разрешаем относительные/произвольные строки для изображения, без строгой URL-валидации
    product_image = serializers.CharField(required=False, allow_blank=True)
    class Meta:
        model = OrderItem
        fields = [
            'product_id', 'product_title', 'product_description', 
            'product_image', 'price', 'quantity', 'has_case', 'film_type'
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'email', 'phone', 'telegram_username', 'total_amount', 'status',
            'delivery_address', 'delivery_method', 'delivery_cost',
            'created_at', 'items'
        ]
        read_only_fields = ['id', 'created_at', 'status']


class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'robokassa_invoice_id', 'amount', 
            'currency', 'status', 'created_at', 'paid_at'
        ]
        read_only_fields = ['id', 'created_at', 'paid_at', 'status']


class CreateOrderSerializer(serializers.Serializer):
    """Сериализатор для создания заказа"""
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    telegram_username = serializers.CharField(max_length=100, required=False, allow_blank=True)
    delivery_address = serializers.CharField(required=False, allow_blank=True)
    delivery_method = serializers.CharField(max_length=100, required=False, allow_blank=True)
    delivery_cost = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    items = OrderItemSerializer(many=True)
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Вычисляем общую сумму заказа
        total_amount = sum(
            float(item['price']) * item['quantity'] 
            for item in items_data
        )
        
        # Добавляем стоимость доставки
        delivery_cost = validated_data.get('delivery_cost', 0)
        total_amount += float(delivery_cost)
        
        # Создаем заказ с вычисленной суммой
        order = Order.objects.create(
            total_amount=total_amount,
            **validated_data
        )
        
        # Создаем товары в заказе
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order
