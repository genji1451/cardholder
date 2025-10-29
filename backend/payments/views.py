import hashlib
import hmac
import logging
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Order, Payment
from .serializers import CreateOrderSerializer, PaymentSerializer
import json
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_order(request):
    """Создание заказа и подготовка к оплате"""
    try:
        logger.info(f"Creating order with data: {request.data}")
        
        # Проверяем настройки Robokassa
        if not settings.ROBOKASSA_LOGIN or not settings.ROBOKASSA_PASSWORD1:
            logger.error("Robokassa settings not configured")
            return Response({
                'error': 'Payment system not configured'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializer = CreateOrderSerializer(data=request.data)
        
        if serializer.is_valid():
            logger.info("Serializer is valid, creating order")
            order = serializer.save()
            logger.info(f"Order created: {order.id}")
            
            # Создаем платеж
            payment = Payment.objects.create(
                order=order,
                robokassa_invoice_id=str(order.id),
                amount=order.total_amount
            )
            
            # Генерируем URL для оплаты
            signature = payment.generate_signature()
        
        robokassa_url = f"https://auth.robokassa.ru/Merchant/Index.aspx"
        if settings.ROBOKASSA_TEST_MODE:
            robokassa_url = f"https://auth.robokassa.ru/Merchant/Index.aspx"
        
        payment_data = {
            'MerchantLogin': settings.ROBOKASSA_LOGIN,
            'OutSum': str(payment.amount),
            'InvId': str(order.id),
            'Description': f"Заказ #{order.id}",
            'SignatureValue': signature,
            'Culture': 'ru',
            'Encoding': 'utf-8',
            'IsTest': 1 if settings.ROBOKASSA_TEST_MODE else 0,
            'SuccessURL': settings.ROBOKASSA_SUCCESS_URL,
            'FailURL': settings.ROBOKASSA_FAIL_URL,
        }
        
            logger.info(f"Payment created: {payment.id}, amount: {payment.amount}")
            
            return Response({
                'order_id': str(order.id),
                'payment_id': payment.id,
                'amount': payment.amount,
                'robokassa_url': robokassa_url,
                'payment_data': payment_data,
                'signature': signature
            }, status=status.HTTP_201_CREATED)
        
        logger.error(f"Serializer validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Unexpected error in create_order: {str(e)}", exc_info=True)
        return Response({
            'error': 'Internal server error',
            'details': str(e) if settings.DEBUG else 'Contact support'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@require_POST
def robokassa_result(request):
    """Обработка уведомления от Robokassa о результате платежа"""
    try:
        # Получаем данные от Robokassa
        out_sum = request.POST.get('OutSum')
        inv_id = request.POST.get('InvId')
        signature = request.POST.get('SignatureValue')
        
        logger.info(f"Robokassa result: OutSum={out_sum}, InvId={inv_id}, Signature={signature}")
        
        # Находим заказ и платеж
        try:
            order = Order.objects.get(id=inv_id)
            payment = Payment.objects.get(order=order)
        except (Order.DoesNotExist, Payment.DoesNotExist):
            logger.error(f"Order or Payment not found for InvId: {inv_id}")
            return HttpResponse("ERROR")
        
        # Проверяем сумму
        if float(out_sum) != float(payment.amount):
            logger.error(f"Amount mismatch: expected {payment.amount}, got {out_sum}")
            return HttpResponse("ERROR")
        
        # Проверяем подпись
        signature_string = f"{out_sum}:{inv_id}:{settings.ROBOKASSA_PASSWORD2}"
        expected_signature = hashlib.md5(signature_string.encode()).hexdigest()
        
        if not hmac.compare_digest(signature.lower(), expected_signature.lower()):
            logger.error(f"Signature mismatch: expected {expected_signature}, got {signature}")
            return HttpResponse("ERROR")
        
        # Обновляем статус
        payment.status = 'success'
        payment.paid_at = timezone.now()
        payment.robokassa_response = dict(request.POST)
        payment.save()
        
        order.status = 'paid'
        order.save()
        
        logger.info(f"Payment successful for order {inv_id}")
        return HttpResponse("OK")
        
    except Exception as e:
        logger.error(f"Error processing Robokassa result: {str(e)}")
        return HttpResponse("ERROR")


@api_view(['GET'])
@permission_classes([AllowAny])
def payment_status(request, order_id):
    """Проверка статуса платежа"""
    try:
        order = Order.objects.get(id=order_id)
        payment = Payment.objects.get(order=order)
        
        return Response({
            'order_id': str(order.id),
            'status': payment.status,
            'amount': payment.amount,
            'paid_at': payment.paid_at
        })
    except (Order.DoesNotExist, Payment.DoesNotExist):
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


def payment_success(request):
    """Страница успешной оплаты"""
    order_id = request.GET.get('InvId')
    context = {
        'order_id': order_id,
        'success': True
    }
    return render(request, 'payments/success.html', context)


def payment_fail(request):
    """Страница неуспешной оплаты"""
    order_id = request.GET.get('InvId')
    context = {
        'order_id': order_id,
        'success': False
    }
    return render(request, 'payments/fail.html', context)