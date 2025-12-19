"""
Задачи для отправки уведомлений пользователям бота
"""

import logging
import asyncio
from asgiref.sync import sync_to_async
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError, Forbidden, BadRequest
from django.conf import settings
from django.utils import timezone
from telegram_bot.models import BotUser, Notification, Break
from telegram_bot.breaks import complete_break

logger = logging.getLogger(__name__)


def send_notification_task(notification_id):
    """
    Синхронная обертка для асинхронной отправки уведомления
    
    Args:
        notification_id: ID уведомления для отправки
    """
    try:
        asyncio.run(send_notification_async(notification_id))
    except Exception as e:
        logger.error(f"Error in send_notification_task: {e}", exc_info=True)
        raise


async def send_notification_async(notification_id):
    """
    Асинхронная отправка уведомления
    
    Args:
        notification_id: ID уведомления для отправки
    """
    try:
        # Получаем уведомление (синхронно через sync_to_async)
        @sync_to_async
        def get_notification():
            return Notification.objects.get(id=notification_id)
        
        notification = await get_notification()
        
        # Проверяем статус
        if notification.status not in ['draft', 'scheduled']:
            logger.warning(f"Notification {notification_id} has status {notification.status}, skipping")
            return
        
        # Обновляем статус
        @sync_to_async
        def update_status():
            notif = Notification.objects.get(id=notification_id)
            notif.status = 'sending'
            notif.save()
            return notif
        
        notification = await update_status()
        
        # Получаем получателей
        @sync_to_async
        def get_recipients_list():
            return get_recipients(notification)
        
        recipients = await get_recipients_list()
        
        @sync_to_async
        def update_total():
            notif = Notification.objects.get(id=notification_id)
            notif.total_recipients = len(recipients)
            notif.save()
            return notif
        
        notification = await update_total()
        
        if not recipients:
            @sync_to_async
            def mark_failed():
                notif = Notification.objects.get(id=notification_id)
                notif.mark_as_failed("Нет получателей")
            
            await mark_failed()
            return
        
        # Создаем бота
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            @sync_to_async
            def mark_failed():
                notif = Notification.objects.get(id=notification_id)
                notif.mark_as_failed("TELEGRAM_BOT_TOKEN не настроен")
            
            await mark_failed()
            return
        
        bot = Bot(token=bot_token)
        
        # Подготавливаем клавиатуру
        reply_markup = None
        if notification.button_text and notification.button_url:
            keyboard = [[InlineKeyboardButton(notification.button_text, url=notification.button_url)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем уведомления
        success_count = 0
        failed_count = 0
        errors = []
        
        for user in recipients:
            try:
                if notification.image:
                    # Отправляем с изображением
                    with open(notification.image.path, 'rb') as photo:
                        await bot.send_photo(
                            chat_id=user.telegram_id,
                            photo=photo,
                            caption=notification.message,
                            parse_mode='HTML',
                            reply_markup=reply_markup
                        )
                else:
                    # Отправляем только текст
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=notification.message,
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
                
                success_count += 1
                logger.info(f"Notification sent to user {user.telegram_id}")
                
            except Forbidden:
                # Пользователь заблокировал бота
                @sync_to_async
                def mark_blocked():
                    u = BotUser.objects.get(id=user.id)
                    u.is_blocked = True
                    u.save()
                
                await mark_blocked()
                failed_count += 1
                logger.warning(f"User {user.telegram_id} blocked the bot")
                
            except BadRequest as e:
                # Неверный запрос (например, неправильный chat_id)
                failed_count += 1
                errors.append(f"User {user.telegram_id}: {str(e)}")
                logger.error(f"Bad request for user {user.telegram_id}: {e}")
                
            except TelegramError as e:
                # Другие ошибки Telegram
                failed_count += 1
                errors.append(f"User {user.telegram_id}: {str(e)}")
                logger.error(f"Telegram error for user {user.telegram_id}: {e}")
                
            except Exception as e:
                # Неожиданные ошибки
                failed_count += 1
                errors.append(f"User {user.telegram_id}: {str(e)}")
                logger.error(f"Unexpected error for user {user.telegram_id}: {e}", exc_info=True)
            
            # Небольшая задержка между отправками (защита от флуда)
            await asyncio.sleep(0.05)
        
        # Обновляем статистику
        @sync_to_async
        def update_stats():
            notif = Notification.objects.get(id=notification_id)
            notif.success_count = success_count
            notif.failed_count = failed_count
            
            if errors:
                notif.error_message = "\n".join(errors[:10])  # Сохраняем первые 10 ошибок
            
            if success_count > 0:
                notif.mark_as_sent()
            else:
                notif.mark_as_failed("Не удалось отправить ни одному пользователю")
        
        await update_stats()
        
        logger.info(
            f"Notification {notification_id} completed: "
            f"{success_count} success, {failed_count} failed"
        )
        
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
        
    except Exception as e:
        logger.error(f"Error sending notification {notification_id}: {e}", exc_info=True)
        try:
            @sync_to_async
            def mark_failed():
                notif = Notification.objects.get(id=notification_id)
                notif.mark_as_failed(str(e))
            
            await mark_failed()
        except:
            pass


def get_recipients(notification):
    """
    Получает список получателей для уведомления
    
    Args:
        notification: Объект Notification
        
    Returns:
        QuerySet пользователей BotUser
    """
    if notification.target_type == 'specific' and notification.target_user:
        # Конкретный пользователь
        return [notification.target_user]
    
    elif notification.target_type == 'active':
        # Только активные пользователи
        return list(BotUser.objects.filter(
            is_active=True,
            is_blocked=False
        ))
    
    else:  # 'all'
        # Все пользователи (кроме заблокировавших бота)
        return list(BotUser.objects.filter(is_blocked=False))


async def send_message_to_user(user_id, message, parse_mode='HTML', reply_markup=None):
    """
    Вспомогательная функция для отправки сообщения конкретному пользователю
    
    Args:
        user_id: Telegram ID пользователя
        message: Текст сообщения
        parse_mode: Режим форматирования (HTML или Markdown)
        reply_markup: Клавиатура
    """
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN не настроен")
            return False
        
        bot = Bot(token=bot_token)
        
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending message to user {user_id}: {e}")
        return False


def check_and_complete_breaks():
    """
    Проверяет и завершает брейки, у которых истёк срок
    
    Эта функция должна вызываться периодически (например, через cron или celery)
    """
    try:
        asyncio.run(check_and_complete_breaks_async())
    except Exception as e:
        logger.error(f"Error in check_and_complete_breaks: {e}", exc_info=True)
        raise


async def check_and_complete_breaks_async():
    """
    Асинхронная проверка и завершение брейков
    """
    try:
        @sync_to_async
        def get_expired_breaks():
            """Получает брейки, у которых истёк срок"""
            now = timezone.now()
            return list(Break.objects.filter(
                status='active',
                end_time__lte=now
            ))
        
        expired_breaks = await get_expired_breaks()
        
        if not expired_breaks:
            logger.debug("No expired breaks found")
            return
        
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN не настроен")
            return
        
        bot = Bot(token=bot_token)
        
        for break_obj in expired_breaks:
            try:
                logger.info(f"Completing break {break_obj.id}: {break_obj.name}")
                await complete_break(break_obj, bot)
            except Exception as e:
                logger.error(f"Error completing break {break_obj.id}: {e}", exc_info=True)
        
        logger.info(f"Completed {len(expired_breaks)} breaks")
        
    except Exception as e:
        logger.error(f"Error in check_and_complete_breaks_async: {e}", exc_info=True)

