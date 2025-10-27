"""
Обновлённый Telegram бот для проверки подлинности карточек
С поддержкой админки и фотографий
"""

import os
import sys
import logging
from asgiref.sync import sync_to_async
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    Application,
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
from telegram_bot.models import VerifiedCard, VerificationLog, BotUser
from telegram_bot.bot_admin import (
    admin_start,
    get_admin_conversation_handler,
    is_admin,
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def get_or_create_user(telegram_user) -> BotUser:
    """
    Получает или создает пользователя бота
    
    Args:
        telegram_user: Объект User из Telegram
        
    Returns:
        BotUser: Объект пользователя из БД
    """
    @sync_to_async
    def get_or_create():
        user, created = BotUser.objects.get_or_create(
            telegram_id=telegram_user.id,
            defaults={
                'username': telegram_user.username or '',
                'first_name': telegram_user.first_name or '',
                'last_name': telegram_user.last_name or '',
                'language_code': telegram_user.language_code or '',
                'is_bot': telegram_user.is_bot,
            }
        )
        
        # Обновляем информацию о пользователе при каждом взаимодействии
        if not created:
            updated = False
            if user.username != (telegram_user.username or ''):
                user.username = telegram_user.username or ''
                updated = True
            if user.first_name != (telegram_user.first_name or ''):
                user.first_name = telegram_user.first_name or ''
                updated = True
            if user.last_name != (telegram_user.last_name or ''):
                user.last_name = telegram_user.last_name or ''
                updated = True
            
            if updated:
                user.save()
            
            # Увеличиваем счетчик взаимодействий
            user.increment_interaction()
        else:
            logger.info(f"New user registered: {user}")
        
        return user
    
    return await get_or_create()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    user_id = user.id
    
    # Регистрируем или обновляем пользователя
    await get_or_create_user(user)
    
    # Проверяем, есть ли параметр с кодом верификации
    if context.args:
        verify_code = context.args[0]
        await verify_card_by_code(update, context, verify_code)
        return
    
    # Проверяем, является ли пользователь админом
    if is_admin(user_id):
        keyboard = [
            [InlineKeyboardButton("🔐 Админ-панель", callback_data="admin_panel")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("❓ Помощь", callback_data="help")],
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = (
        f"👋 Привет, {user.first_name}!\n\n"
        "🎴 Я бот для проверки подлинности коллекционных карт.\n\n"
        "🔍 <b>Как проверить карту:</b>\n"
        "Отсканируйте QR-код на упаковке карты камерой телефона "
        "и перейдите по ссылке.\n\n"
    )
    
    if is_admin(user_id):
        welcome_message += (
            "🔐 <b>Вы - администратор!</b>\n"
            "Используйте /admin для управления картами."
        )
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def admin_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback для админ-панели"""
    query = update.callback_query
    await query.answer()
    
    # Регистрируем или обновляем пользователя
    await get_or_create_user(query.from_user)
    
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.edit_message_text("❌ У вас нет прав администратора.")
        return
    
    keyboard = [
        [InlineKeyboardButton("➕ Добавить новую карту", callback_data="add_card")],
        [InlineKeyboardButton("📋 Мои карты", callback_data="my_cards")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🔐 <b>Админ-панель</b>\n\n"
        "Добро пожаловать в панель управления картами!\n\n"
        "Выберите действие:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def verify_card_by_code(update: Update, context: ContextTypes.DEFAULT_TYPE, verify_code: str) -> None:
    """
    Проверка подлинности карты по коду верификации
    
    Args:
        update: Объект обновления Telegram
        context: Контекст бота
        verify_code: Код верификации из QR-кода
    """
    try:
        # Ищем верифицированную карту по коду
        @sync_to_async
        def get_card_and_increment():
            card = VerifiedCard.objects.get(
                verification_code=verify_code,
                is_active=True
            )
            # Увеличиваем счётчик проверок
            card.verification_count += 1
            card.save()
            
            # Записываем в лог
            VerificationLog.objects.create(
                verified_card=card,
                telegram_user_id=update.effective_user.id,
                telegram_username=update.effective_user.username or ''
            )
            
            return card
        
        verified_card = await get_card_and_increment()
        
        # Формируем информацию о карте
        card_info = (
            "✅ Карта подтверждена системой защиты\n\n"
            f"🎴 <b>{verified_card.card_name}</b>\n\n"
        )
        
        if verified_card.description:
            card_info += f"📝 <b>Описание:</b>\n{verified_card.description}\n\n"
        
        card_info += (
            f"🔍 Проверено: <b>{verified_card.verification_count}</b> раз\n"
            f"📅 Добавлена: <b>{verified_card.created_at.strftime('%d.%m.%Y')}</b>\n\n"
            "🛡️ <b>Карта подтверждена системой защиты</b>"
        )
        
        # Создаём клавиатуру
        keyboard = [
            [InlineKeyboardButton("🔗 Поделиться", callback_data=f"share_{verified_card.id}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем фотографии
        media = []
        
        # Добавляем оригинальное фото
        if verified_card.photo_original:
            try:
                photo_path = verified_card.photo_original.path
                if os.path.exists(photo_path):
                    with open(photo_path, 'rb') as photo:
                        media.append(InputMediaPhoto(
                            media=photo.read(),
                            caption="📸 Оригинальная карта"
                        ))
            except Exception as e:
                logger.warning(f"Could not load original photo: {e}")
        
        # Добавляем фото в упаковке
        if verified_card.photo_packaged:
            try:
                photo_path = verified_card.photo_packaged.path
                if os.path.exists(photo_path):
                    with open(photo_path, 'rb') as photo:
                        media.append(InputMediaPhoto(
                            media=photo.read(),
                            caption="📦 Карта в упаковке"
                        ))
            except Exception as e:
                logger.warning(f"Could not load packaged photo: {e}")
        
        # Отправляем медиа-группу если есть фото
        if media:
            await update.message.reply_media_group(media=media)
        
        # Отправляем текстовую информацию
        await update.message.reply_text(
            card_info,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        
        logger.info(f"Card {verified_card.id} verified by user {update.effective_user.id}")
        
    except VerifiedCard.DoesNotExist:
        # Карта не найдена
        error_message = (
            "❌ <b>Карта не найдена</b>\n\n"
            "Эта карта не зарегистрирована в системе или была деактивирована.\n\n"
            "⚠️ <b>Возможные причины:</b>\n"
            "  • Карта является подделкой\n"
            "  • QR-код повреждён\n"
            "  • Карта ещё не добавлена в систему\n\n"
            "🛡️ Рекомендуем связаться с продавцом."
        )
        
        await update.message.reply_text(error_message, parse_mode='HTML')
        logger.warning(f"Verification failed for code: {verify_code}")
        
    except Exception as e:
        logger.error(f"Error verifying card: {e}", exc_info=True)
        await update.message.reply_text(
            "😔 Произошла ошибка при проверке карты. Пожалуйста, попробуйте позже.",
        )


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback для помощи"""
    query = update.callback_query
    await query.answer()
    
    # Регистрируем или обновляем пользователя
    await get_or_create_user(query.from_user)
    
    help_text = (
        "📖 <b>Как пользоваться ботом:</b>\n\n"
        "1️⃣ Найдите QR-код на упаковке карты\n"
        "2️⃣ Отсканируйте его камерой телефона\n"
        "3️⃣ Перейдите по ссылке\n"
        "4️⃣ Получите информацию о карте и фото\n\n"
        "✅ <b>Если карта подлинная, вы увидите:</b>\n"
        "  • Фотографии карты (оригинал и в упаковке)\n"
        "  • Название и описание\n"
        "  • Статус подлинности\n\n"
        "❌ <b>Если карта не найдена:</b>\n"
        "Возможно, это подделка или карта не зарегистрирована.\n\n"
        "⚠️ Будьте внимательны при покупке!"
    )
    
    await query.edit_message_text(help_text, parse_mode='HTML')


async def share_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback для кнопки поделиться"""
    query = update.callback_query
    await query.answer()
    
    # Регистрируем или обновляем пользователя
    await get_or_create_user(query.from_user)
    
    data = query.data
    verified_card_id = int(data.split("_")[1])
    
    try:
        @sync_to_async
        def get_card():
            return VerifiedCard.objects.get(id=verified_card_id)
        
        verified_card = await get_card()
        bot_username = context.bot.username
        share_url = verified_card.get_bot_link(bot_username)
        
        share_text = (
            f"🔗 <b>Ссылка для проверки карты:</b>\n\n"
            f"<code>{share_url}</code>\n\n"
            f"Отправьте эту ссылку, чтобы другие могли проверить подлинность карты."
        )
        
        await query.message.reply_text(share_text, parse_mode='HTML')
        
    except VerifiedCard.DoesNotExist:
        await query.message.reply_text("❌ Карта не найдена")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик неизвестных команд"""
    # Регистрируем или обновляем пользователя
    await get_or_create_user(update.effective_user)
    
    await update.message.reply_text(
        "🤔 Я не понимаю эту команду.\n\n"
        "Используйте:\n"
        "/start - Главное меню\n"
        "/admin - Админ-панель (только для администраторов)\n"
        "/help - Помощь"
    )


def main() -> None:
    """Запуск бота"""
    # Получаем токен из настроек Django
    token = settings.TELEGRAM_BOT_TOKEN
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN не настроен в settings.py")
        return
    
    # Создаём приложение
    application = Application.builder().token(token).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_start))
    
    # Обработчики callback'ов (ДОЛЖНЫ БЫТЬ ПЕРЕД ConversationHandler!)
    application.add_handler(CallbackQueryHandler(admin_panel_callback, pattern='^admin_panel$'))
    application.add_handler(CallbackQueryHandler(help_callback, pattern='^help$'))
    application.add_handler(CallbackQueryHandler(share_callback, pattern='^share_'))
    
    # Добавляем ConversationHandler для админки (после callback handlers)
    application.add_handler(get_admin_conversation_handler())
    
    # Обработчик неизвестных команд (должен быть последним)
    application.add_handler(MessageHandler(filters.COMMAND | filters.TEXT, unknown_command))
    
    # Запускаем бота
    logger.info("🤖 Бот запущен и готов к работе...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

