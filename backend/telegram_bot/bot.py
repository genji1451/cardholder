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

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings
from apps.cards.models import Card
from telegram_bot.models import VerifiedCard
from telegram_bot.utils import get_card_image_path, format_card_info

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Проверяем, есть ли параметр с ID карты в deep link
    if context.args:
        verify_code = context.args[0]
        await verify_card(update, context, verify_code)
        return
    
    welcome_message = (
        f"👋 Привет, {user.first_name}!\n\n"
        "Я бот для проверки подлинности карточек.\n\n"
        "🔍 Отсканируйте QR-код на вашей карте, "
        "чтобы проверить её подлинность и получить информацию.\n\n"
        "❓ Команды:\n"
        "/help - Помощь\n"
        "/info - О боте"
    )
    
    await update.message.reply_text(welcome_message)


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
    
    # Обработчик callback'ов от inline кнопок
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Обработчик неизвестных команд (должен быть последним)
    application.add_handler(MessageHandler(filters.COMMAND | filters.TEXT, unknown_command))
    
    # Запускаем бота
    logger.info("🤖 Бот запущен и готов к работе...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

