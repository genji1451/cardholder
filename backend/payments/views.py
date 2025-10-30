import hashlib
import hmac
import logging
import asyncio
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

logger = logging.getLogger(__name__)


async def send_order_notification(order, items_data, telegram_username=None):
    """Отправка уведомления о новом заказе в Telegram"""
    try:
        from telegram import Bot
        
        bot_token = settings.TELEGRAM_BOT_TOKEN
        channel_id = settings.TELEGRAM_CHANNEL_ID
        
        logger.info(f"Starting order notification. Bot token: {bot_token[:10] if bot_token else 'None'}..., Channel ID: {channel_id}")
        
        if not bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN не настроен, пропускаем отправку уведомления")
            return
        
        if not channel_id:
            logger.warning("TELEGRAM_CHANNEL_ID не настроен, пропускаем отправку уведомления")
            return
        
        bot = Bot(token=bot_token)
        
        # Формируем сообщение о заказе
        items_text = "\n".join([
            f"  • {item.get('product_title', 'Товар')} x{item.get('quantity', 1)} - {item.get('price', 0) * item.get('quantity', 1)}₽"
            for item in items_data
        ])
        
        message = f"""🛍️ <b>Новый заказ #{order.id}</b>

👤 <b>Покупатель:</b>
  Email: {order.email}
  Телефон: {order.phone if order.phone else 'Не указан'}
  {"  Telegram: @" + telegram_username if telegram_username else ""}

📦 <b>Товары:</b>
{items_text}

💰 <b>Сумма:</b>
  Товары: {order.total_amount - order.delivery_cost}₽
  Доставка: {"Бесплатно" if order.delivery_cost == 0 else str(order.delivery_cost) + "₽"}
  <b>Итого: {order.total_amount}₽</b>

🚚 <b>Доставка:</b>
  Способ: {order.delivery_method if order.delivery_method else 'Не указан'}
  Адрес: {order.delivery_address if order.delivery_address else 'Не указан'}
"""
        
        # Подготавливаем chat_id: убираем @ если есть, оставляем как есть для числовых ID
        chat_id = channel_id.lstrip('@')
        logger.info(f"Attempting to send message to chat_id: {chat_id}")
        
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"✅ Order notification sent to Telegram channel: {channel_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send order notification to Telegram: {str(e)}")
            logger.error(f"Error details: chat_id={chat_id}, channel_id={channel_id}")
            
    except ImportError as e:
        logger.error(f"Failed to import telegram library: {str(e)}")
    except Exception as e:
        logger.error(f"Error sending order notification: {str(e)}", exc_info=True)


def send_order_notification_sync(order, items_data, telegram_username=None):
    """Синхронная обертка для отправки уведомления"""
    try:
        asyncio.run(send_order_notification(order, items_data, telegram_username))
    except Exception as e:
        logger.error(f"Error in send_order_notification_sync: {str(e)}")


@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def create_order(request):
    """Создание заказа и подготовка к оплате"""
    # Обработка OPTIONS запроса для CORS preflight
    if request.method == 'OPTIONS':
        response = Response(status=status.HTTP_200_OK)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
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
            
            # Сохраняем данные товаров из запроса для формирования описания
            items_data = request.data.get('items', [])
            telegram_username = request.data.get('telegram_username', '')
            
            order = serializer.save()
            logger.info(f"Order created: {order.id}")
            
            # Отправляем уведомление о новом заказе в Telegram (асинхронно, не блокируем ответ)
            try:
                send_order_notification_sync(order, items_data, telegram_username)
            except Exception as e:
                logger.error(f"Failed to send order notification: {str(e)}")
                # Не прерываем создание заказа из-за ошибки уведомления
            
            # Форматируем сумму для Robokassa (убираем лишние нули, но оставляем минимум .00)
            amount = float(order.total_amount)
            # Убеждаемся, что сумма минимум 1 рубль (минимальная сумма для Robokassa)
            if amount < 1:
                amount = 1
            # Форматируем с сохранением .00 для сумм меньше 100 рублей
            if amount < 100 and amount >= 1:
                amount_str = f"{amount:.2f}"
            else:
                amount_str = f"{amount:.2f}".rstrip('0').rstrip('.')
            if not amount_str:
                amount_str = "1.00"
            
            # Создаем платеж
            payment = Payment.objects.create(
                order=order,
                robokassa_invoice_id=str(order.id),  # Временно используем order.id
                amount=order.total_amount
            )
            
            # Используем payment.id как InvId (числовой ID для совместимости с Robokassa)
            inv_id = str(payment.id)
            
            # Обновляем robokassa_invoice_id
            payment.robokassa_invoice_id = inv_id
            payment.save()
            
            # Генерируем подпись с правильными параметрами для Robokassa
            signature_string = f"{settings.ROBOKASSA_LOGIN}:{amount_str}:{inv_id}:{settings.ROBOKASSA_PASSWORD1}"
            signature = hashlib.md5(signature_string.encode()).hexdigest()
            
            logger.info(f"Robokassa signature: {signature_string} -> {signature}")
            
            robokassa_url = "https://auth.robokassa.ru/Merchant/Index.aspx"
            
            # Формируем описание заказа с товарами, контактами и адресом
            # Robokassa ограничивает Description до 100 символов, делаем компактно
            # Используем данные из запроса, так как товары уже созданы в сериализаторе
            try:
                items_list = []
                # Пробуем получить товары из БД (они должны быть созданы)
                order_items = order.items.all()
                if order_items.exists():
                    for item in order_items:
                        items_list.append(f"{item.product_title} x{item.quantity}")
                else:
                    # Если товары еще не сохранены, используем сохраненные данные из запроса
                    for item_data in items_data:
                        title = item_data.get('product_title', 'Товар')
                        quantity = item_data.get('quantity', 1)
                        items_list.append(f"{title} x{quantity}")
                
                # Собираем информацию для описания
                description_parts = []
                
                # Товары (первые 30 символов)
                if items_list:
                    items_str = ", ".join(items_list)[:30]
                    if items_str:
                        description_parts.append(f"Товары: {items_str}")
                
                # Email (первые 20 символов)
                if order.email:
                    email_str = order.email[:20]
                    description_parts.append(f"Email: {email_str}")
                
                # Адрес доставки (первые 20 символов)
                if order.delivery_address:
                    address_str = order.delivery_address[:20]
                    description_parts.append(f"Адрес: {address_str}")
                
                # Ник в телеграм (если указан)
                telegram_username = getattr(order, 'telegram_username', None)
                if telegram_username:
                    telegram_str = telegram_username[:15]
                    description_parts.append(f"TG: {telegram_str}")
                
                # Если ничего не добавилось, используем ID заказа
                if not description_parts:
                    description = f"Заказ {str(order.id)[:50]}"
                else:
                    description = " | ".join(description_parts)
                    # Ограничиваем до 100 символов (лимит Robokassa)
                    if len(description) > 100:
                        description = description[:97] + "..."
                        
            except Exception as e:
                logger.error(f"Error creating description: {str(e)}")
                # Fallback: простое описание
                description = f"Заказ {str(order.id)[:50]}"
            
            payment_data = {
                'MerchantLogin': settings.ROBOKASSA_LOGIN,
                'OutSum': amount_str,
                'InvId': inv_id,
                'Description': description,
                'SignatureValue': signature,
                'Culture': 'ru',
                'Encoding': 'utf-8',
            }
            
            # Добавляем IsTest только если тестовый режим включен
            if settings.ROBOKASSA_TEST_MODE:
                payment_data['IsTest'] = '1'
            
            # Добавляем URL только если они настроены
            if hasattr(settings, 'ROBOKASSA_SUCCESS_URL') and settings.ROBOKASSA_SUCCESS_URL:
                payment_data['SuccessURL'] = settings.ROBOKASSA_SUCCESS_URL
            if hasattr(settings, 'ROBOKASSA_FAIL_URL') and settings.ROBOKASSA_FAIL_URL:
                payment_data['FailURL'] = settings.ROBOKASSA_FAIL_URL
            
            logger.info(f"Payment created: {payment.id}, amount: {payment.amount}")
            
            response = Response({
                'order_id': str(order.id),
                'payment_id': payment.id,
                'amount': payment.amount,
                'robokassa_url': robokassa_url,
                'payment_data': payment_data,
                'signature': signature
            }, status=status.HTTP_201_CREATED)
            
            # Добавляем CORS заголовки в ответ
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            
            return response
        
        logger.error(f"Serializer validation failed: {serializer.errors}")
        response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        response['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error in create_order: {str(e)}", exc_info=True)
        response = Response({
            'error': 'Internal server error',
            'details': str(e) if settings.DEBUG else 'Contact support'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response['Access-Control-Allow-Origin'] = '*'
        return response


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
        
        # Находим платеж по robokassa_invoice_id (InvId теперь = payment.id)
        try:
            payment = Payment.objects.get(robokassa_invoice_id=inv_id)
            order = payment.order
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for InvId: {inv_id}")
            return HttpResponse("ERROR")
        
        # Проверяем сумму (сравниваем как числа, учитывая возможные различия в форматировании)
        expected_amount = float(payment.amount)
        received_amount = float(out_sum)
        if abs(expected_amount - received_amount) > 0.01:  # Разрешаем небольшую погрешность
            logger.error(f"Amount mismatch: expected {expected_amount}, got {received_amount}")
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


@csrf_exempt
def payment_success(request):
    """Страница успешной оплаты - редирект на фронтенд"""
    # Получаем InvId из GET или POST (Robokassa может отправлять POST)
    order_id = request.GET.get('InvId') or request.POST.get('InvId')
    
    # Если InvId есть, ищем payment и обновляем статус
    if order_id:
        try:
            payment = Payment.objects.get(robokassa_invoice_id=order_id)
            if payment.status == 'pending':
                payment.status = 'success'
                payment.paid_at = timezone.now()
                payment.save()
                
                order = payment.order
                if order.status == 'pending':
                    order.status = 'paid'
                    order.save()
                
                logger.info(f"Payment marked as success: {order_id}")
        except Payment.DoesNotExist:
            logger.warning(f"Payment not found for InvId: {order_id}")
    
    # Редиректим на фронтенд с параметром InvId
    frontend_url = 'https://portfolio.cards/payment/success/'
    if order_id:
        frontend_url += f'?InvId={order_id}'
    
    return redirect(frontend_url)


@csrf_exempt
def payment_fail(request):
    """Страница неуспешной оплаты - редирект на фронтенд"""
    # Получаем InvId из GET или POST
    order_id = request.GET.get('InvId') or request.POST.get('InvId')
    
    # Если InvId есть, обновляем статус платежа
    if order_id:
        try:
            payment = Payment.objects.get(robokassa_invoice_id=order_id)
            if payment.status == 'pending':
                payment.status = 'failed'
                payment.save()
                logger.info(f"Payment marked as failed: {order_id}")
        except Payment.DoesNotExist:
            logger.warning(f"Payment not found for InvId: {order_id}")
    
    # Редиректим на фронтенд с параметром InvId
    frontend_url = 'https://portfolio.cards/payment/fail/'
    if order_id:
        frontend_url += f'?InvId={order_id}'
    
    return redirect(frontend_url)