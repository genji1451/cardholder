"""
Модуль для работы с брейками (аукционами на группы карт)

Брейк - это формат аукциона, где пользователи делают ставки на группы карт.
После окончания администратор открывает бустеры, и победитель получает все карты из группы.
"""

import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from telegram_bot.models import (
    BotUser,
    Break,
    BreakGroup,
    BreakBid,
    BreakWinner,
)

logger = logging.getLogger(__name__)

# Константы
EXTEND_TIME_MINUTES = 5  # На сколько минут продлевать брейк при новой ставке
MIN_TIME_BEFORE_END_TO_EXTEND = 5  # Минимальное время до окончания для продления


def get_or_create_bot_user(user):
    """
    Получает или создаёт пользователя бота
    
    Args:
        user: Объект пользователя из Telegram Update
        
    Returns:
        BotUser: Объект пользователя бота
    """
    bot_user, created = BotUser.objects.get_or_create(
        telegram_id=user.id,
        defaults={
            'username': user.username or '',
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'language_code': user.language_code or 'ru',
            'is_bot': user.is_bot or False,
        }
    )
    
    if not created:
        # Обновляем данные пользователя
        bot_user.username = user.username or bot_user.username
        bot_user.first_name = user.first_name or bot_user.first_name
        bot_user.last_name = user.last_name or bot_user.last_name
        bot_user.language_code = user.language_code or bot_user.language_code
        bot_user.last_interaction = timezone.now()
        bot_user.increment_interaction()
        bot_user.save()
    
    return bot_user


async def breaks_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Главное меню брейков
    
    Показывает список активных брейков.
    """
    user = update.effective_user
    bot_user = get_or_create_bot_user(user)
    
    # Получаем активные брейки
    active_breaks = Break.objects.filter(
        status='active',
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    ).order_by('-created_at')
    
    if not active_breaks.exists():
        message = (
            "📦 <b>Брейки</b>\n\n"
            "В данный момент нет активных брейков.\n\n"
            "Следите за обновлениями в канале!"
        )
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        return
    
    # Формируем список брейков
    message = "📦 <b>Активные брейки</b>\n\n"
    keyboard = []
    
    for break_obj in active_breaks[:10]:  # Ограничиваем 10 брейками
        time_left = break_obj.end_time - timezone.now()
        hours = int(time_left.total_seconds() // 3600)
        minutes = int((time_left.total_seconds() % 3600) // 60)
        
        message += f"🎯 <b>{break_obj.name}</b>\n"
        message += f"⏰ Осталось: {hours}ч {minutes}м\n\n"
        
        keyboard.append([
            InlineKeyboardButton(
                f"🎯 {break_obj.name}",
                callback_data=f"break_view_{break_obj.id}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )


async def break_view(update: Update, context: ContextTypes.DEFAULT_TYPE, break_id: int) -> None:
    """
    Просмотр конкретного брейка
    
    Показывает описание брейка и список групп.
    """
    try:
        break_obj = Break.objects.prefetch_related('groups').get(id=break_id)
    except Break.DoesNotExist:
        await update.callback_query.answer("Брейк не найден", show_alert=True)
        return
    
    # Формируем сообщение
    message = f"🎯 <b>{break_obj.name}</b>\n\n"
    message += f"{break_obj.description}\n\n"
    
    if break_obj.checklist_url:
        message += f"📋 <a href='{break_obj.checklist_url}'>Чек-лист коллекции</a>\n\n"
    
    # Время до окончания
    if break_obj.status == 'active':
        time_left = break_obj.end_time - timezone.now()
        if time_left.total_seconds() > 0:
            hours = int(time_left.total_seconds() // 3600)
            minutes = int((time_left.total_seconds() % 3600) // 60)
            message += f"⏰ Осталось времени: {hours}ч {minutes}м\n\n"
        else:
            message += "⏰ Брейк завершён\n\n"
    
    # Список групп
    groups = break_obj.get_active_groups()
    if groups.exists():
        message += "<b>Группы:</b>\n"
        keyboard = []
        
        for group in groups:
            current_bid = group.get_current_bid()
            message += f"\n{group.order + 1}. <b>{group.name}</b> - {current_bid}₽"
            
            keyboard.append([
                InlineKeyboardButton(
                    f"{group.order + 1}. {group.name} ({current_bid}₽)",
                    callback_data=f"break_group_{group.id}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="breaks_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        message += "Группы пока не добавлены."
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="breaks_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        message,
        parse_mode='HTML',
        reply_markup=reply_markup,
        disable_web_page_preview=False
    )


async def break_group_view(update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int) -> None:
    """
    Просмотр группы брейка
    
    Показывает название группы, текущую ставку и историю ставок.
    """
    try:
        group = BreakGroup.objects.select_related('break_obj').prefetch_related(
            'bids__user'
        ).get(id=group_id)
    except BreakGroup.DoesNotExist:
        await update.callback_query.answer("Группа не найдена", show_alert=True)
        return
    
    break_obj = group.break_obj
    
    # Проверяем, активен ли брейк
    if break_obj.status != 'active' or not break_obj.is_active():
        await update.callback_query.answer(
            "Этот брейк уже завершён",
            show_alert=True
        )
        return
    
    # Формируем сообщение
    message = f"🎯 <b>{group.name}</b>\n\n"
    message += f"Брейк: {break_obj.name}\n\n"
    
    current_bid = group.get_current_bid()
    min_next_bid = group.get_min_next_bid()
    
    message += f"💰 <b>Текущая ставка:</b> {current_bid}₽\n"
    message += f"📈 <b>Минимальная следующая:</b> {min_next_bid}₽\n\n"
    
    # История ставок (последние 10)
    recent_bids = group.bids.filter(is_valid=True).select_related('user').order_by('-amount', '-created_at')[:10]
    
    if recent_bids.exists():
        message += "<b>Последние ставки:</b>\n"
        for bid in recent_bids:
            user_name = bid.user.get_full_name()
            time_str = bid.created_at.strftime('%H:%M')
            message += f"• {user_name}: {bid.amount}₽ ({time_str})\n"
    
    # Кнопки
    keyboard = [
        [InlineKeyboardButton(
            f"💰 Сделать ставку ({min_next_bid}₽)",
            callback_data=f"break_bid_{group.id}"
        )],
        [InlineKeyboardButton("◀️ Назад", callback_data=f"break_view_{break_obj.id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )


async def break_bid_start(update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int) -> None:
    """
    Начало процесса ставки
    
    Запрашивает у пользователя сумму ставки.
    """
    try:
        group = BreakGroup.objects.select_related('break_obj').get(id=group_id)
    except BreakGroup.DoesNotExist:
        await update.callback_query.answer("Группа не найдена", show_alert=True)
        return
    
    break_obj = group.break_obj
    
    # Проверяем, активен ли брейк
    if break_obj.status != 'active' or not break_obj.is_active():
        await update.callback_query.answer(
            "Этот брейк уже завершён",
            show_alert=True
        )
        return
    
    min_next_bid = group.get_min_next_bid()
    
    message = (
        f"💰 <b>Сделать ставку</b>\n\n"
        f"Группа: <b>{group.name}</b>\n"
        f"Текущая ставка: {group.get_current_bid()}₽\n"
        f"Минимальная ставка: <b>{min_next_bid}₽</b>\n\n"
        f"Введите сумму ставки (только число, например: {int(min_next_bid)}):"
    )
    
    keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data=f"break_group_{group.id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    
    # Сохраняем group_id в контексте для обработки следующего сообщения
    context.user_data['break_bid_group_id'] = group_id


async def break_bid_process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработка ставки пользователя
    
    Валидирует сумму и создаёт ставку.
    """
    if 'break_bid_group_id' not in context.user_data:
        return
    
    group_id = context.user_data['break_bid_group_id']
    
    try:
        group = BreakGroup.objects.select_related('break_obj').get(id=group_id)
    except BreakGroup.DoesNotExist:
        await update.message.reply_text("❌ Группа не найдена")
        del context.user_data['break_bid_group_id']
        return
    
    break_obj = group.break_obj
    
    # Проверяем, активен ли брейк
    if break_obj.status != 'active' or not break_obj.is_active():
        await update.message.reply_text("❌ Этот брейк уже завершён")
        del context.user_data['break_bid_group_id']
        return
    
    # Парсим сумму
    try:
        amount = Decimal(update.message.text.replace(',', '.').strip())
    except (ValueError, AttributeError):
        await update.message.reply_text(
            "❌ Неверный формат суммы. Введите число, например: 500"
        )
        return
    
    # Валидация суммы
    min_next_bid = group.get_min_next_bid()
    
    if amount < min_next_bid:
        await update.message.reply_text(
            f"❌ Минимальная ставка: {min_next_bid}₽\n"
            f"Вы ввели: {amount}₽"
        )
        return
    
    # Создаём ставку
    user = update.effective_user
    bot_user = get_or_create_bot_user(user)
    
    try:
        with transaction.atomic():
            # Делаем предыдущие ставки недействительными
            BreakBid.objects.filter(
                group=group,
                is_valid=True
            ).update(is_valid=False)
            
            # Создаём новую ставку
            bid = BreakBid.objects.create(
                group=group,
                user=bot_user,
                amount=amount,
                is_valid=True
            )
            
            # Проверяем, нужно ли продлевать время
            time_until_end = (break_obj.end_time - timezone.now()).total_seconds() / 60
            
            if time_until_end <= MIN_TIME_BEFORE_END_TO_EXTEND:
                break_obj.extend_end_time(EXTEND_TIME_MINUTES)
                logger.info(
                    f"Брейк {break_obj.id} продлён на {EXTEND_TIME_MINUTES} минут "
                    f"из-за новой ставки"
                )
            
            # Уведомляем предыдущего лидера (если был)
            previous_bid = BreakBid.objects.filter(
                group=group,
                is_valid=False
            ).order_by('-created_at').first()
            
            if previous_bid and previous_bid.user.telegram_id != bot_user.telegram_id:
                await notify_bid_outbid(
                    context.bot,
                    previous_bid.user,
                    break_obj,
                    group,
                    amount
                )
            
            # Обновляем комментарий в канале
            await update_channel_comment(context.bot, break_obj)
            
            # Подтверждение пользователю
            message = (
                f"✅ <b>Ставка принята!</b>\n\n"
                f"Группа: {group.name}\n"
                f"Ваша ставка: <b>{amount}₽</b>\n\n"
                f"Вы сейчас лидируете в этой группе."
            )
            
            keyboard = [
                [InlineKeyboardButton(
                    "◀️ К группе",
                    callback_data=f"break_group_{group.id}"
                )],
                [InlineKeyboardButton(
                    "📦 К брейку",
                    callback_data=f"break_view_{break_obj.id}"
                )]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            
            logger.info(
                f"Ставка создана: пользователь {bot_user.telegram_id}, "
                f"группа {group.id}, сумма {amount}₽"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при создании ставки: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при создании ставки. Попробуйте позже."
        )
    
    finally:
        # Очищаем контекст
        del context.user_data['break_bid_group_id']


async def notify_bid_outbid(
    bot,
    user: BotUser,
    break_obj: Break,
    group: BreakGroup,
    new_amount: Decimal
) -> None:
    """
    Уведомляет пользователя, что его ставку перебили
    
    Args:
        bot: Экземпляр бота Telegram
        user: Пользователь, чью ставку перебили
        break_obj: Брейк
        group: Группа
        new_amount: Новая ставка
    """
    try:
        message = (
            f"⚠️ <b>Вашу ставку перебили</b>\n\n"
            f"Брейк: {break_obj.name}\n"
            f"Группа: {group.name}\n"
            f"Текущая ставка: <b>{new_amount}₽</b>\n\n"
            f"Вы можете сделать новую ставку!"
        )
        
        keyboard = [[InlineKeyboardButton(
            "💰 Сделать ставку",
            callback_data=f"break_bid_{group.id}"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await bot.send_message(
            chat_id=user.telegram_id,
            text=message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        
        logger.info(f"Уведомление отправлено пользователю {user.telegram_id} о перебитой ставке")
        
    except TelegramError as e:
        logger.error(f"Ошибка при отправке уведомления пользователю {user.telegram_id}: {e}")


async def update_channel_comment(bot, break_obj: Break) -> None:
    """
    Обновляет комментарий под постом в канале с актуальными ставками
    
    Args:
        bot: Экземпляр бота Telegram
        break_obj: Брейк
    """
    if not break_obj.channel_id or not break_obj.channel_post_id:
        return
    
    try:
        # Получаем все группы с текущими ставками
        groups = break_obj.get_active_groups()
        
        if not groups.exists():
            return
        
        # Формируем текст комментария
        comment_lines = []
        for group in groups.order_by('order', 'id'):
            current_bid = group.get_current_bid()
            comment_lines.append(f"{group.order + 1} - {int(current_bid)}")
        
        comment_text = "\n".join(comment_lines)
        
        # Отправляем новый комментарий (не редактируем старый)
        await bot.send_message(
            chat_id=break_obj.channel_id,
            text=comment_text,
            reply_to_message_id=break_obj.channel_post_id
        )
        
        logger.info(f"Комментарий обновлён для брейка {break_obj.id}")
        
    except TelegramError as e:
        logger.error(f"Ошибка при обновлении комментария для брейка {break_obj.id}: {e}")


async def complete_break(break_obj: Break, bot) -> None:
    """
    Завершает брейк и определяет победителей
    
    Args:
        break_obj: Брейк для завершения
        bot: Экземпляр бота Telegram
    """
    try:
        with transaction.atomic():
            # Определяем победителей для каждой группы
            groups = break_obj.get_active_groups()
            
            for group in groups:
                winning_bid = group.bids.filter(is_valid=True).order_by('-amount', '-created_at').first()
                
                if winning_bid:
                    # Создаём запись о победителе
                    winner, created = BreakWinner.objects.get_or_create(
                        group=group,
                        defaults={
                            'user': winning_bid.user,
                            'winning_bid': winning_bid,
                        }
                    )
                    
                    if created:
                        # Уведомляем победителя
                        await notify_winner(bot, winner)
            
            # Меняем статус брейка
            break_obj.status = 'completed'
            break_obj.save()
            
            logger.info(f"Брейк {break_obj.id} завершён")
            
    except Exception as e:
        logger.error(f"Ошибка при завершении брейка {break_obj.id}: {e}")


async def notify_winner(bot, winner: BreakWinner) -> None:
    """
    Уведомляет победителя группы
    
    Args:
        bot: Экземпляр бота Telegram
        winner: Победитель группы
    """
    try:
        message = (
            f"🎉 <b>Поздравляем! Вы победили!</b>\n\n"
            f"Брейк: {winner.group.break_obj.name}\n"
            f"Группа: <b>{winner.group.name}</b>\n"
            f"Ваша ставка: {winner.winning_bid.amount}₽\n\n"
            f"Брейк завершён. Пожалуйста, свяжитесь с администратором "
            f"для оплаты и доставки."
        )
        
        await bot.send_message(
            chat_id=winner.user.telegram_id,
            text=message,
            parse_mode='HTML'
        )
        
        winner.notified = True
        winner.save(update_fields=['notified'])
        
        logger.info(f"Победитель {winner.user.telegram_id} уведомлён о победе в группе {winner.group.id}")
        
    except TelegramError as e:
        logger.error(f"Ошибка при уведомлении победителя {winner.user.telegram_id}: {e}")


def format_break_post(break_obj: Break, bot_username: str) -> tuple[str, InlineKeyboardMarkup]:
    """
    Форматирует пост для публикации в канале
    
    Args:
        break_obj: Брейк
        bot_username: Username бота
        
    Returns:
        tuple: (текст поста, клавиатура с кнопкой)
    """
    message = f"🎯 <b>{break_obj.name}</b>\n\n"
    message += f"{break_obj.description}\n\n"
    
    if break_obj.checklist_url:
        message += f"📋 <a href='{break_obj.checklist_url}'>Чек-лист коллекции</a>\n\n"
    
    start_time_str = break_obj.start_time.strftime('%d.%m.%Y %H:%M')
    end_time_str = break_obj.end_time.strftime('%d.%m.%Y %H:%M')
    
    message += f"⏰ Начало: {start_time_str}\n"
    message += f"⏰ Окончание: {end_time_str}\n\n"
    message += "Участвуйте в брейке и выигрывайте карты!"
    
    # Кнопка для участия
    button_url = f"https://t.me/{bot_username}?start=break_{break_obj.id}"
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎯 Участвовать в брейке", url=button_url)
    ]])
    
    return message, keyboard