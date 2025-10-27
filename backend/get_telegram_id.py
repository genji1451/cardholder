#!/usr/bin/env python3
"""
Простой скрипт для получения вашего Telegram ID
Запустите этот бот, напишите ему /start и получите свой ID
"""

import os
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8089087655:AAH3ZobI5iV5ZTENxyLqQdyDV5nXGfAXTU0")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет ID пользователя"""
    user = update.effective_user
    
    message = (
        f"👋 Привет, {user.first_name}!\n\n"
        f"🆔 <b>Ваш Telegram ID:</b> <code>{user.id}</code>\n\n"
        f"📝 Скопируйте этот ID и добавьте в:\n"
        f"<code>backend/telegram_bot/bot_admin.py</code>\n\n"
        f"В строку:\n"
        f"<code>ADMIN_IDS = [{user.id}]</code>"
    )
    
    await update.message.reply_text(message, parse_mode='HTML')
    
    logger.info(f"User ID: {user.id}, Username: @{user.username or 'N/A'}")


def main():
    """Запуск бота"""
    print("🤖 Запускаю бота для получения Telegram ID...")
    print("📱 Откройте бота в Telegram и напишите /start")
    print("🔑 Вы получите свой ID\n")
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    try:
        application.run_polling()
    except KeyboardInterrupt:
        print("\n✅ Бот остановлен")


if __name__ == '__main__':
    main()

