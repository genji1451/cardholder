"""
Административная часть Telegram бота
Позволяет администраторам добавлять карты и генерировать QR-коды
"""

import os
import sys
from io import BytesIO
from asgiref.sync import sync_to_async
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings
from telegram_bot.models import VerifiedCard
from telegram_bot.utils import create_card_qr_code, get_qr_codes_directory

# Состояния для ConversationHandler
WAITING_FOR_PHOTO_1 = 1
WAITING_FOR_NAME = 2
WAITING_FOR_DESCRIPTION = 3
WAITING_FOR_PHOTO_2 = 4

# ID администраторов (добавьте свой Telegram ID)
ADMIN_IDS = [1918066256]


def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    # Если список пуст, первый пользователь становится админом
    if not ADMIN_IDS:
        return True
    return user_id in ADMIN_IDS


async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало процесса добавления карты"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ У вас нет прав администратора.\n"
            "Этот бот доступен только для администраторов."
        )
        return ConversationHandler.END
    
    keyboard = [
        [InlineKeyboardButton("➕ Добавить новую карту", callback_data="add_card")],
        [InlineKeyboardButton("📋 Мои карты", callback_data="my_cards")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔐 <b>Админ-панель</b>\n\n"
        "Добро пожаловать в панель управления картами!\n\n"
        "Выберите действие:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    
    return ConversationHandler.END


async def add_card_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало процесса добавления карты"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📸 <b>Шаг 1/4: Фото карты</b>\n\n"
        "Отправьте фотографию карты (оригинал, до упаковки).\n\n"
        "💡 Советы:\n"
        "• Хорошее освещение\n"
        "• Карта в фокусе\n"
        "• Видны все детали\n\n"
        "Или отправьте /cancel для отмены",
        parse_mode='HTML'
    )
    
    return WAITING_FOR_PHOTO_1


async def receive_photo_1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение первого фото карты"""
    photo = update.message.photo[-1]  # Берём самое большое фото
    
    # Сохраняем file_id в контексте
    context.user_data['photo_1_file_id'] = photo.file_id
    
    await update.message.reply_text(
        "✅ Фото карты получено!\n\n"
        "📝 <b>Шаг 2/4: Название карты</b>\n\n"
        "Отправьте название карты.\n"
        "Например: <code>Человек-Паук #1 Ультра</code>\n\n"
        "Или отправьте /cancel для отмены",
        parse_mode='HTML'
    )
    
    return WAITING_FOR_NAME


async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение названия карты"""
    card_name = update.message.text.strip()
    context.user_data['card_name'] = card_name
    
    await update.message.reply_text(
        f"✅ Название: <b>{card_name}</b>\n\n"
        "📝 <b>Шаг 3/4: Описание карты</b>\n\n"
        "Отправьте описание карты для покупателей.\n"
        "Укажите:\n"
        "• Серию\n"
        "• Редкость\n"
        "• Состояние\n"
        "• Особенности\n\n"
        "Или отправьте /skip чтобы пропустить",
        parse_mode='HTML'
    )
    
    return WAITING_FOR_DESCRIPTION


async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение описания карты"""
    if update.message.text == '/skip':
        context.user_data['description'] = ''
    else:
        context.user_data['description'] = update.message.text.strip()
    
    try:
        # Создаём верифицированную карту (в синхронном контексте)
        @sync_to_async
        def create_card():
            return VerifiedCard.objects.create(
                card_name=context.user_data['card_name'],
                description=context.user_data.get('description', '')
            )
        
        verified_card = await create_card()
        
        # Скачиваем и сохраняем первое фото
        photo_file = await context.bot.get_file(context.user_data['photo_1_file_id'])
        photo_bytes = await photo_file.download_as_bytearray()
        
        # Сохраняем фото (в синхронном контексте)
        @sync_to_async
        def save_photo(card_id):
            from django.core.files.base import ContentFile
            card = VerifiedCard.objects.get(id=card_id)
            card.photo_original.save(
                f'card_{card.id}_original.jpg',
                ContentFile(bytes(photo_bytes)),
                save=True
            )
            return card
        
        verified_card = await save_photo(verified_card.id)
        
        # Генерируем QR-код
        bot_username = settings.TELEGRAM_BOT_USERNAME
        qr_buffer = create_card_qr_code(verified_card, bot_username)
        
        # Сохраняем ID карты для следующего шага
        context.user_data['verified_card_id'] = verified_card.id
        
        # Отправляем QR-код с коротким caption
        qr_buffer.seek(0)  # Возвращаем указатель в начало
        await update.message.reply_photo(
            photo=qr_buffer,
            caption=f"📱 QR-код для карты: {verified_card.card_name}"
        )
        
        # Отправляем подробную информацию отдельным сообщением
        await update.message.reply_text(
            "✅ <b>Карта создана!</b>\n\n"
            f"🎴 Название: <b>{verified_card.card_name}</b>\n"
            f"🔑 Код: <code>{verified_card.verification_code}</code>\n\n"
            "🖨️ <b>Что делать дальше:</b>\n"
            "1. Распечатайте этот QR-код\n"
            "2. Наклейте QR на кейс с картой\n"
            "3. Сфотографируйте упакованную карту\n\n"
            "📸 <b>Шаг 4/4: Фото упакованной карты</b>\n\n"
            "Отправьте фото карты с наклеенным QR-кодом\n"
            "Или отправьте /skip если фото не нужно",
            parse_mode='HTML'
        )
        
        return WAITING_FOR_PHOTO_2
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка при создании карты: {str(e)}\n\n"
            "Попробуйте снова с /admin"
        )
        context.user_data.clear()
        return ConversationHandler.END


async def receive_photo_2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение второго фото (упакованная карта)"""
    verified_card_id = context.user_data.get('verified_card_id')
    
    if not verified_card_id:
        await update.message.reply_text("❌ Ошибка: карта не найдена")
        return ConversationHandler.END
    
    if update.message.text == '/skip':
        # Завершаем без второго фото
        @sync_to_async
        def get_card():
            return VerifiedCard.objects.get(id=verified_card_id)
        
        verified_card = await get_card()
        bot_link = verified_card.get_bot_link(settings.TELEGRAM_BOT_USERNAME)
        
        await update.message.reply_text(
            "✅ <b>Карта успешно добавлена!</b>\n\n"
            f"🎴 {verified_card.card_name}\n"
            f"🔑 Код: <code>{verified_card.verification_code}</code>\n\n"
            f"🔗 Ссылка для проверки:\n"
            f"<code>{bot_link}</code>\n\n"
            "Клиенты смогут сканировать QR-код и проверять подлинность карты!\n\n"
            "Используйте /admin для возврата в меню",
            parse_mode='HTML'
        )
    else:
        # Сохраняем второе фото
        photo = update.message.photo[-1]
        photo_file = await context.bot.get_file(photo.file_id)
        photo_bytes = await photo_file.download_as_bytearray()
        
        @sync_to_async
        def save_packaged_photo():
            from django.core.files.base import ContentFile
            card = VerifiedCard.objects.get(id=verified_card_id)
            card.photo_packaged.save(
                f'card_{card.id}_packaged.jpg',
                ContentFile(bytes(photo_bytes)),
                save=True
            )
            return card
        
        verified_card = await save_packaged_photo()
        bot_link = verified_card.get_bot_link(settings.TELEGRAM_BOT_USERNAME)
        
        await update.message.reply_text(
            "✅ <b>Карта успешно добавлена!</b>\n\n"
            f"🎴 {verified_card.card_name}\n"
            f"🔑 Код: <code>{verified_card.verification_code}</code>\n\n"
            f"🔗 Ссылка для проверки:\n"
            f"<code>{bot_link}</code>\n\n"
            "✅ Оба фото загружены!\n"
            "Клиенты смогут видеть карту до и после упаковки.\n\n"
            "Используйте /admin для возврата в меню",
            parse_mode='HTML'
        )
    
    # Очищаем контекст
    context.user_data.clear()
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена процесса"""
    context.user_data.clear()
    
    await update.message.reply_text(
        "❌ Операция отменена.\n\n"
        "Используйте /admin для возврата в меню"
    )
    
    return ConversationHandler.END


async def my_cards(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать список карт"""
    query = update.callback_query
    await query.answer()
    
    @sync_to_async
    def get_cards():
        return list(VerifiedCard.objects.filter(is_active=True).order_by('-created_at')[:10])
    
    cards = await get_cards()
    
    if not cards:
        await query.edit_message_text(
            "📋 <b>Мои карты</b>\n\n"
            "У вас пока нет добавленных карт.\n\n"
            "Используйте /admin для добавления карты",
            parse_mode='HTML'
        )
        return  # Это нормально - выход из функции
    
    message = "📋 <b>Последние 10 карт:</b>\n\n"
    
    for i, card in enumerate(cards, 1):
        status = "✅" if card.is_active else "❌"
        message += (
            f"{i}. {status} <b>{card.card_name}</b>\n"
            f"   Код: <code>{card.verification_code[:8]}...</code>\n"
            f"   Проверок: {card.verification_count}\n\n"
        )
    
    message += "Используйте /admin для возврата в меню"
    
    await query.edit_message_text(message, parse_mode='HTML')


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать статистику"""
    query = update.callback_query
    await query.answer()
    
    @sync_to_async
    def get_stats():
        total_cards = VerifiedCard.objects.count()
        active_cards = VerifiedCard.objects.filter(is_active=True).count()
        total_checks = sum(VerifiedCard.objects.values_list('verification_count', flat=True) or [0])
        top_cards = list(VerifiedCard.objects.order_by('-verification_count')[:3])
        return total_cards, active_cards, total_checks, top_cards
    
    total_cards, active_cards, total_checks, top_cards = await get_stats()
    
    message = (
        "📊 <b>Статистика</b>\n\n"
        f"🎴 Всего карт: <b>{total_cards}</b>\n"
        f"✅ Активных: <b>{active_cards}</b>\n"
        f"❌ Неактивных: <b>{total_cards - active_cards}</b>\n"
        f"🔍 Всего проверок: <b>{total_checks}</b>\n\n"
    )
    
    if total_cards > 0:
        avg_checks = total_checks / total_cards
        message += f"📈 Среднее проверок на карту: <b>{avg_checks:.1f}</b>\n\n"
    
    # Топ-3 карты
    if top_cards:
        message += "🏆 <b>Топ-3 карты:</b>\n"
        for i, card in enumerate(top_cards, 1):
            message += f"{i}. {card.card_name} - {card.verification_count} проверок\n"
    
    message += "\nИспользуйте /admin для возврата в меню"
    
    await query.edit_message_text(message, parse_mode='HTML')


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Роутер для callback кнопок"""
    query = update.callback_query
    data = query.data
    
    if data == "add_card":
        return await add_card_start(update, context)
    elif data == "my_cards":
        await my_cards(update, context)
        return ConversationHandler.END
    elif data == "stats":
        await stats(update, context)
        return ConversationHandler.END
    
    return ConversationHandler.END


# Создаём ConversationHandler для процесса добавления карты
def get_admin_conversation_handler():
    """Возвращает ConversationHandler для админских команд"""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(callback_router, pattern='^(add_card|my_cards|stats)$')
        ],
        states={
            WAITING_FOR_PHOTO_1: [
                MessageHandler(filters.PHOTO, receive_photo_1),
                CommandHandler('cancel', cancel),
            ],
            WAITING_FOR_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name),
                CommandHandler('cancel', cancel),
            ],
            WAITING_FOR_DESCRIPTION: [
                MessageHandler(filters.TEXT, receive_description),
                CommandHandler('cancel', cancel),
            ],
            WAITING_FOR_PHOTO_2: [
                MessageHandler(filters.PHOTO | filters.TEXT, receive_photo_2),
                CommandHandler('cancel', cancel),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False,  # Важно для callback'ов
        per_chat=True,
        per_user=True,
    )

