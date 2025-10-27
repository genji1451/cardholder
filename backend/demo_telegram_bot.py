#!/usr/bin/env python3
"""
Демонстрационный скрипт для Telegram бота
Показывает основные возможности системы
"""

import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from apps.cards.models import Card, Series
from telegram_bot.models import VerifiedCard, VerificationLog
from telegram_bot.utils import create_card_qr_code, generate_qr_code, get_qr_codes_directory


def print_header(text):
    """Красивый заголовок"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def demo_info():
    """Показать информацию о системе"""
    print_header("📊 ИНФОРМАЦИЯ О СИСТЕМЕ")
    
    # Статистика по картам
    total_cards = Card.objects.count()
    total_series = Series.objects.count()
    print(f"🎴 Всего карт в базе: {total_cards}")
    print(f"📚 Всего серий: {total_series}")
    
    # Статистика по верификациям
    total_verified = VerifiedCard.objects.count()
    active_verified = VerifiedCard.objects.filter(is_active=True).count()
    total_checks = sum(VerifiedCard.objects.values_list('verification_count', flat=True) or [0])
    
    print(f"\n✅ Верифицированных карт: {total_verified}")
    print(f"   Активных: {active_verified}")
    print(f"   Деактивированных: {total_verified - active_verified}")
    print(f"\n🔍 Всего проверок: {total_checks}")
    
    if total_verified > 0:
        avg_checks = total_checks / total_verified
        print(f"   Среднее проверок на карту: {avg_checks:.2f}")
    
    # Логи
    total_logs = VerificationLog.objects.count()
    print(f"\n📝 Записей в логах: {total_logs}")


def demo_create_verification():
    """Демо создания верификации"""
    print_header("➕ СОЗДАНИЕ ВЕРИФИКАЦИИ")
    
    # Находим первую карту без верификации
    verified_card_ids = VerifiedCard.objects.values_list('card_id', flat=True)
    unverified_cards = Card.objects.exclude(id__in=verified_card_ids)
    
    if not unverified_cards.exists():
        print("⚠️  Все карты уже верифицированы!")
        print("Используем существующую карту для демонстрации...")
        card = Card.objects.first()
        if not card:
            print("❌ В базе нет карт!")
            return None
    else:
        card = unverified_cards.first()
    
    # Создаём верификацию
    verified_card, created = VerifiedCard.objects.get_or_create(
        card=card,
        defaults={
            'notes': 'Создано демо-скриптом',
            'owner_info': 'Demo Owner'
        }
    )
    
    if created:
        print(f"✅ Создана верификация для карты:")
    else:
        print(f"ℹ️  Верификация уже существует для карты:")
    
    print(f"   Название: {card.title}")
    print(f"   Номер: #{card.number}")
    print(f"   Серия: {card.series.title}")
    print(f"   Код верификации: {verified_card.verification_code}")
    
    # Генерируем ссылку на бота
    bot_username = settings.TELEGRAM_BOT_USERNAME
    bot_link = verified_card.get_bot_link(bot_username)
    print(f"\n🔗 Ссылка на бота:")
    print(f"   {bot_link}")
    
    return verified_card


def demo_generate_qr(verified_card):
    """Демо генерации QR-кода"""
    if not verified_card:
        print("⚠️  Нет верифицированной карты для генерации QR-кода")
        return
    
    print_header("📱 ГЕНЕРАЦИЯ QR-КОДА")
    
    bot_username = settings.TELEGRAM_BOT_USERNAME
    qr_dir = get_qr_codes_directory()
    
    # Генерируем QR-код
    card = verified_card.card
    qr_filename = f'demo_card_{card.series.number}_{card.number}.png'
    qr_path = os.path.join(qr_dir, qr_filename)
    
    try:
        create_card_qr_code(verified_card, bot_username, save_path=qr_path)
        print(f"✅ QR-код успешно создан!")
        print(f"   Файл: {qr_path}")
        print(f"   Размер: {os.path.getsize(qr_path)} байт")
        
        # Проверяем существование файла
        if os.path.exists(qr_path):
            print(f"\n💾 QR-код сохранён и готов к использованию!")
            print(f"   Откройте файл: open {qr_path}")
        
    except Exception as e:
        print(f"❌ Ошибка при создании QR-кода: {e}")


def demo_top_cards():
    """Показать топ популярных карт"""
    print_header("🏆 ТОП-5 ПОПУЛЯРНЫХ КАРТ")
    
    top_cards = VerifiedCard.objects.select_related('card', 'card__series').order_by(
        '-verification_count'
    )[:5]
    
    if not top_cards.exists():
        print("⚠️  Нет верифицированных карт")
        return
    
    for i, vc in enumerate(top_cards, 1):
        print(f"{i}. {vc.card.title} #{vc.card.number}")
        print(f"   Проверок: {vc.verification_count}")
        print(f"   Статус: {'✅ Активна' if vc.is_active else '❌ Деактивирована'}")
        print()


def demo_bot_commands():
    """Показать доступные команды бота"""
    print_header("🤖 КОМАНДЫ TELEGRAM БОТА")
    
    print("Команды для пользователей:")
    print("  /start - Начать работу с ботом / Проверить карту")
    print("  /help  - Помощь по использованию")
    print("  /info  - Информация о системе проверки")
    
    print("\nДля запуска бота используйте:")
    print("  python manage.py run_telegram_bot")
    print("  или")
    print("  ./run_telegram_bot.sh")


def demo_api_endpoints():
    """Показать API endpoints"""
    print_header("🌐 API ENDPOINTS")
    
    base_url = "http://localhost:8000"
    
    print("Публичные (без авторизации):")
    print(f"  GET {base_url}/api/telegram-bot/verified-cards/verify/?code=XXX")
    print()
    
    print("Приватные (требуют JWT токен):")
    print(f"  GET  {base_url}/api/telegram-bot/verified-cards/")
    print(f"  POST {base_url}/api/telegram-bot/verified-cards/")
    print(f"  GET  {base_url}/api/telegram-bot/verified-cards/{{id}}/")
    print(f"  GET  {base_url}/api/telegram-bot/verified-cards/{{id}}/qr_code/")
    print(f"  GET  {base_url}/api/telegram-bot/verified-cards/statistics/")
    print()
    
    print("Для тестирования используйте curl или Postman")


def main():
    """Главная функция"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║                                                       ║")
    print("║     🎴  TELEGRAM BOT - ДЕМОНСТРАЦИЯ СИСТЕМЫ  🤖      ║")
    print("║                                                       ║")
    print("╚═══════════════════════════════════════════════════════╝")
    
    try:
        # 1. Информация о системе
        demo_info()
        
        # 2. Создание верификации
        verified_card = demo_create_verification()
        
        # 3. Генерация QR-кода
        demo_generate_qr(verified_card)
        
        # 4. Топ карт
        demo_top_cards()
        
        # 5. Команды бота
        demo_bot_commands()
        
        # 6. API endpoints
        demo_api_endpoints()
        
        # Финальное сообщение
        print_header("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
        print("Система готова к использованию!")
        print()
        print("Следующие шаги:")
        print("  1. Запустите бота: ./run_telegram_bot.sh")
        print("  2. Создайте верификации: python manage.py create_verified_cards --generate-qr")
        print("  3. Откройте админку: http://localhost:8000/admin/")
        print("  4. Проверьте QR-коды в: backend/media/qr_codes/")
        print()
        print("📚 Документация:")
        print("  - QUICK_START_TELEGRAM_BOT.md - Быстрый старт")
        print("  - TELEGRAM_BOT_README.md - Полная документация")
        print("  - TELEGRAM_BOT_CHEATSHEET.md - Шпаргалка")
        print()
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

