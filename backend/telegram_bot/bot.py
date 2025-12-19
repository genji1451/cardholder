"""
Основной модуль Telegram бота для проверки подлинности карточек
"""

import os
import sys
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from telegram.error import TelegramError
from django.utils import timezone

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings
from apps.cards.models import Card
from telegram_bot.models import VerifiedCard
from telegram_bot.utils import get_card_image_path, format_card_info
from telegram_bot.breaks import (
    breaks_menu,
    break_view,
    break_group_view,
    break_bid_start,
    break_bid_process,
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Проверяем, есть ли параметр в deep link
    if context.args:
        arg = context.args[0]
        
        # Проверяем, это код верификации карты или ссылка на брейк
        if arg.startswith('break_'):
            # Это ссылка на брейк
            try:
                break_id = int(arg.replace('break_', ''))
                await break_view_from_deeplink(update, context, break_id)
            except ValueError:
                await verify_card(update, context, arg)
        else:
            # Это код верификации карты
            await verify_card(update, context, arg)
        return
    
    welcome_message = (
        f"👋 Привет, {user.first_name}!\n\n"
        "Я бот для проверки подлинности карточек.\n\n"
        "🔍 Отсканируйте QR-код на вашей карте, "
        "чтобы проверить её подлинность и получить информацию.\n\n"
        "❓ Команды:\n"
        "/help - Помощь\n"
        "/info - О боте\n"
        "/breaks - 📦 Брейки\n"
    )
    
    # Создаем клавиатуру с кнопками
    keyboard = [
        [InlineKeyboardButton("📦 Брейки", callback_data="breaks_menu")],
        [InlineKeyboardButton("ℹ️ О боте", callback_data="info_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)


async def break_view_from_deeplink(update: Update, context: ContextTypes.DEFAULT_TYPE, break_id: int) -> None:
    """
    Обработка deep link на брейк
    
    Открывает брейк напрямую из ссылки.
    """
    from telegram_bot.models import Break
    
    try:
        break_obj = Break.objects.prefetch_related('groups').get(id=break_id)
    except Break.DoesNotExist:
        await update.message.reply_text("❌ Брейк не найден")
        return
    
    # Формируем сообщение аналогично break_view, но для обычного сообщения
    message = f"🎯 <b>{break_obj.name}</b>\n\n"
    message += f"{break_obj.description}\n\n"
    
    if break_obj.checklist_url:
        message += f"📋 <a href='{break_obj.checklist_url}'>Чек-лист коллекции</a>\n\n"
    
    if break_obj.status == 'active':
        time_left = break_obj.end_time - timezone.now()
        if time_left.total_seconds() > 0:
            hours = int(time_left.total_seconds() // 3600)
            minutes = int((time_left.total_seconds() % 3600) // 60)
            message += f"⏰ Осталось времени: {hours}ч {minutes}м\n\n"
    
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
        
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        message += "Группы пока не добавлены."
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message,
        parse_mode='HTML',
        reply_markup=reply_markup,
        disable_web_page_preview=False
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_text = (
        "📖 <b>Как пользоваться ботом:</b>\n\n"
        "1️⃣ Найдите QR-код на вашей карточке\n"
        "2️⃣ Отсканируйте его камерой телефона\n"
        "3️⃣ Перейдите по ссылке - вы автоматически попадёте в этот бот\n"
        "4️⃣ Получите информацию о подлинности карты и её фото\n\n"
        "✅ Если карта подлинная, вы увидите:\n"
        "  • Фотографию карты\n"
        "  • Название и номер карты\n"
        "  • Серию и редкость\n"
        "  • Статус подлинности\n\n"
        "❌ Если карта не найдена или поддельная, "
        "вы получите соответствующее уведомление.\n\n"
        "⚠️ Будьте внимательны при покупке карт у неофициальных продавцов!"
    )
    
    await update.message.reply_text(help_text, parse_mode='HTML')


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /info"""
    info_text = (
        "ℹ️ <b>О системе проверки подлинности</b>\n\n"
        "Каждая оригинальная карточка имеет уникальный QR-код, "
        "который невозможно подделать.\n\n"
        "🔐 QR-код содержит зашифрованную информацию:\n"
        "  • Уникальный идентификатор карты\n"
        "  • Серийный номер\n"
        "  • Информацию о серии\n\n"
        "Эта система защищает вас от подделок и помогает "
        "проверить подлинность карты в любой момент.\n\n"
        "💼 Для владельцев коллекций: вы можете использовать "
        "этот бот для управления своим инвентарём."
    )
    
    await update.message.reply_text(info_text, parse_mode='HTML')


async def verify_card(update: Update, context: ContextTypes.DEFAULT_TYPE, verify_code: str) -> None:
    """
    Проверка подлинности карты по коду верификации
    
    Args:
        update: Объект обновления Telegram
        context: Контекст бота
        verify_code: Код верификации из QR-кода
    """
    try:
        # Ищем верифицированную карту по коду
        verified_card = VerifiedCard.objects.select_related('card', 'card__series').get(
            verification_code=verify_code,
            is_active=True
        )
        
        card = verified_card.card
        
        # Формируем информацию о карте
        card_info = format_card_info(card, verified_card)
        
        # Путь к изображению карты
        image_path = get_card_image_path(card)
        
        # Создаём клавиатуру с дополнительными опциями
        keyboard = [
            [
                InlineKeyboardButton("📊 Подробнее о карте", callback_data=f"details_{verified_card.id}"),
            ],
            [
                InlineKeyboardButton("🔗 Поделиться", callback_data=f"share_{verified_card.id}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем фото с информацией
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=card_info,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
        else:
            # Если фото нет, отправляем только текст
            await update.message.reply_text(
                card_info,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        
        # Увеличиваем счётчик проверок
        verified_card.verification_count += 1
        verified_card.save()
        
        logger.info(f"Card {card.id} verified by user {update.effective_user.id}")
        
    except VerifiedCard.DoesNotExist:
        # Карта не найдена или неактивна
        error_message = (
            "❌ <b>Карта не найдена</b>\n\n"
            "Эта карта не зарегистрирована в системе или была деактивирована.\n\n"
            "⚠️ <b>Возможные причины:</b>\n"
            "  • Карта является подделкой\n"
            "  • QR-код повреждён\n"
            "  • Карта ещё не добавлена в систему\n\n"
            "🛡️ Рекомендуем связаться с продавцом для проверки подлинности."
        )
        
        await update.message.reply_text(error_message, parse_mode='HTML')
        logger.warning(f"Verification failed for code: {verify_code}")
        
    except Exception as e:
        logger.error(f"Error verifying card: {e}")
        await update.message.reply_text(
            "😔 Произошла ошибка при проверке карты. Пожалуйста, попробуйте позже.",
            parse_mode='HTML'
        )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на inline кнопки"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "main_menu":
        await start(update, context)
        return
    elif data == "info_menu":
        await info_command_inline(update, context)
        return
    elif data == "breaks_menu":
        await breaks_menu(update, context)
        return
    
    # Break callbacks
    if data.startswith("break_view_"):
        break_id = int(data.replace("break_view_", ""))
        await break_view(update, context, break_id)
        return
    elif data.startswith("break_group_"):
        group_id = int(data.replace("break_group_", ""))
        await break_group_view(update, context, group_id)
        return
    elif data.startswith("break_bid_"):
        group_id = int(data.replace("break_bid_", ""))
        await break_bid_start(update, context, group_id)
        return
    
    # Card verification callbacks
    if data.startswith("details_"):
        verified_card_id = int(data.split("_")[1])
        try:
            verified_card = VerifiedCard.objects.select_related('card', 'card__series').get(id=verified_card_id)
            card = verified_card.card
            
            details_text = (
                f"📊 <b>Подробная информация</b>\n\n"
                f"🎴 <b>Название:</b> {card.title}\n"
                f"🔢 <b>Номер:</b> #{card.number}\n"
                f"📚 <b>Серия:</b> {card.series.title}\n"
                f"💎 <b>Редкость:</b> {card.get_rarity_display()}\n"
                f"💰 <b>Базовая цена:</b> {card.base_price_rub} ₽\n"
                f"🔍 <b>Проверок:</b> {verified_card.verification_count}\n"
                f"📅 <b>Создана:</b> {verified_card.created_at.strftime('%d.%m.%Y')}\n"
            )
            
            if card.notes:
                details_text += f"\n📝 <b>Примечания:</b> {card.notes}"
            
            await query.edit_message_caption(
                caption=details_text,
                parse_mode='HTML'
            )
            
        except VerifiedCard.DoesNotExist:
            await query.edit_message_caption(
                caption="❌ Карта не найдена",
                parse_mode='HTML'
            )
    
    elif data.startswith("share_"):
        verified_card_id = int(data.split("_")[1])
        try:
            verified_card = VerifiedCard.objects.get(id=verified_card_id)
            bot_username = context.bot.username
            share_url = f"https://t.me/{bot_username}?start={verified_card.verification_code}"
            
            share_text = (
                f"🔗 <b>Ссылка для проверки карты:</b>\n\n"
                f"<code>{share_url}</code>\n\n"
                f"Отправьте эту ссылку, чтобы другие могли проверить подлинность карты."
            )
            
            await query.message.reply_text(share_text, parse_mode='HTML')
            
        except VerifiedCard.DoesNotExist:
            await query.message.reply_text(
                "❌ Карта не найдена",
                parse_mode='HTML'
            )


async def info_command_inline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик inline кнопки info"""
    query = update.callback_query
    await query.answer()
    
    info_text = (
        "ℹ️ <b>О системе проверки подлинности</b>\n\n"
        "Каждая оригинальная карточка имеет уникальный QR-код, "
        "который невозможно подделать.\n\n"
        "🔐 QR-код содержит зашифрованную информацию:\n"
        "  • Уникальный идентификатор карты\n"
        "  • Серийный номер\n"
        "  • Информацию о серии\n\n"
        "Эта система защищает вас от подделок и помогает "
        "проверить подлинность карты в любой момент.\n\n"
        "💼 Для владельцев коллекций: вы можете использовать "
        "этот бот для управления своим инвентарём."
    )
    
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(info_text, parse_mode='HTML', reply_markup=reply_markup)


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    # Проверяем, ожидается ли ставка в брейке
    if 'break_bid_group_id' in context.user_data:
        await break_bid_process(update, context)
        return
    
    # Иначе обрабатываем как неизвестную команду
    await unknown_command(update, context)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик неизвестных команд и сообщений"""
    await update.message.reply_text(
        "🤔 Я не понимаю эту команду.\n\n"
        "Отсканируйте QR-код на вашей карте или используйте /help для помощи."
    )


def main() -> None:
    """Запуск бота"""
    # Получаем токен из настроек Django
    token = settings.TELEGRAM_BOT_TOKEN
    
    if not token or token == "YOUR_BOT_TOKEN":
        logger.error("TELEGRAM_BOT_TOKEN не настроен в settings.py")
        return
    
    # Создаём приложение
    application = Application.builder().token(token).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("breaks", breaks_menu))
    
    # Обработчик callback'ов от inline кнопок
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Обработчик ставок в брейках (обрабатывает текстовые сообщения со ставками)
    # Должен быть перед общим обработчиком текста
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_text_message
    ))
    
    # Обработчик неизвестных команд (должен быть последним)
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # Запускаем бота
    logger.info("🤖 Бот запущен и готов к работе...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

