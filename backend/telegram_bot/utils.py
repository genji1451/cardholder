"""
Утилиты для работы с Telegram ботом и QR-кодами
"""

import os
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from apps.cards.models import Card
from telegram_bot.models import VerifiedCard


def generate_qr_code(data: str, size: int = 300) -> BytesIO:
    """
    Генерирует QR-код с данными
    
    Args:
        data: Данные для кодирования в QR
        size: Размер QR-кода в пикселях
    
    Returns:
        BytesIO объект с изображением QR-кода
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size), Image.LANCZOS)
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer


def generate_qr_code_with_logo(data: str, logo_path: str = None, size: int = 300) -> BytesIO:
    """
    Генерирует QR-код с логотипом в центре
    
    Args:
        data: Данные для кодирования
        logo_path: Путь к логотипу (опционально)
        size: Размер QR-кода
    
    Returns:
        BytesIO объект с изображением
    """
    # Создаём базовый QR-код
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    img = img.resize((size, size), Image.LANCZOS)
    
    # Добавляем логотип если есть
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path)
            
            # Вычисляем размер логотипа (20% от QR-кода)
            logo_size = int(size * 0.2)
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
            
            # Вычисляем позицию для центрирования
            logo_pos = ((size - logo_size) // 2, (size - logo_size) // 2)
            
            # Создаём белый фон для логотипа
            logo_bg = Image.new('RGB', (logo_size + 20, logo_size + 20), 'white')
            logo_bg_pos = ((size - logo_size - 20) // 2, (size - logo_size - 20) // 2)
            
            img.paste(logo_bg, logo_bg_pos)
            img.paste(logo, logo_pos, logo if logo.mode == 'RGBA' else None)
        except Exception as e:
            print(f"Ошибка при добавлении логотипа: {e}")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer


def create_card_qr_code(verified_card: VerifiedCard, bot_username: str, 
                        save_path: str = None) -> BytesIO:
    """
    Создаёт QR-код для конкретной карты
    
    Args:
        verified_card: Объект верифицированной карты
        bot_username: Username Telegram бота
        save_path: Путь для сохранения (опционально)
    
    Returns:
        BytesIO с изображением QR-кода
    """
    # Формируем ссылку на бота
    bot_link = verified_card.get_bot_link(bot_username)
    
    # Генерируем QR-код
    qr_buffer = generate_qr_code(bot_link, size=400)
    
    # Сохраняем если указан путь
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(qr_buffer.getvalue())
        qr_buffer.seek(0)
    
    return qr_buffer


def get_card_image_path(card: Card) -> str:
    """
    Возвращает путь к изображению карты
    
    Args:
        card: Объект карты
    
    Returns:
        Полный путь к изображению карты
    """
    # Предполагаем, что изображения хранятся в структуре:
    # frontend/public/images/spiderman/series{X}/card_{Y}.svg (или .png)
    
    base_path = os.path.join(
        settings.BASE_DIR.parent,
        'frontend',
        'public',
        'images',
        'spiderman',
        f'series{card.series.number}'
    )
    
    # Проверяем разные форматы изображений
    for ext in ['.svg', '.png', '.jpg', '.jpeg', '.webp']:
        image_path = os.path.join(base_path, f'card_{card.number}{ext}')
        if os.path.exists(image_path):
            return image_path
    
    # Если не найдено, возвращаем путь по умолчанию
    return os.path.join(base_path, f'card_{card.number}.svg')


def format_card_info(card: Card, verified_card: VerifiedCard) -> str:
    """
    Форматирует информацию о карте для отображения в Telegram
    
    Args:
        card: Объект карты
        verified_card: Объект верифицированной карты
    
    Returns:
        Отформатированная строка с информацией
    """
    status_emoji = "✅" if verified_card.is_active else "❌"
    rarity_emoji = {
        "о": "⚪️",  # Обычная
        "ск": "🔵",  # Средняя карта
        "ук": "🟣",  # Ультра карта
    }.get(card.rarity, "⚪️")
    
    info = (
        f"{status_emoji} <b>ОРИГИНАЛЬНАЯ КАРТА</b>\n\n"
        f"🎴 <b>{card.title}</b>\n"
        f"🔢 Номер: <b>#{card.number}</b>\n"
        f"📚 Серия: <b>{card.series.title}</b>\n"
        f"{rarity_emoji} Редкость: <b>{card.get_rarity_display()}</b>\n"
    )
    
    if card.base_price_rub:
        info += f"💰 Базовая цена: <b>{card.base_price_rub} ₽</b>\n"
    
    info += f"\n🔍 Проверено: <b>{verified_card.verification_count}</b> раз\n"
    
    if verified_card.notes:
        info += f"\n📝 {verified_card.notes}"
    
    info += "\n\n🛡️ Карта подтверждена системой защиты."
    
    return info


def get_qr_codes_directory():
    """Возвращает директорию для хранения QR-кодов"""
    qr_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)
    return qr_dir


def generate_printable_card_label(verified_card: VerifiedCard, bot_username: str) -> BytesIO:
    """
    Генерирует изображение метки для печати на карте
    Включает QR-код и базовую информацию
    
    Args:
        verified_card: Объект верифицированной карты
        bot_username: Username бота
    
    Returns:
        BytesIO с изображением метки
    """
    card = verified_card.card
    
    # Размеры метки (например, для стандартной карты)
    label_width = 600
    label_height = 200
    
    # Создаём изображение
    img = Image.new('RGB', (label_width, label_height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Генерируем QR-код
    qr_buffer = create_card_qr_code(verified_card, bot_username)
    qr_img = Image.open(qr_buffer)
    qr_img = qr_img.resize((180, 180), Image.LANCZOS)
    
    # Вставляем QR-код слева
    img.paste(qr_img, (10, 10))
    
    # Добавляем текстовую информацию справа
    try:
        # Пытаемся использовать системный шрифт
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except:
        # Если не получилось, используем дефолтный
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Текст
    text_x = 210
    draw.text((text_x, 20), card.title, fill='black', font=font_large)
    draw.text((text_x, 55), f"Серия: {card.series.title}", fill='black', font=font_medium)
    draw.text((text_x, 85), f"Номер: #{card.number}", fill='black', font=font_medium)
    draw.text((text_x, 115), f"Редкость: {card.get_rarity_display()}", fill='black', font=font_medium)
    draw.text((text_x, 155), "Отсканируйте для проверки", fill='gray', font=font_small)
    
    # Конвертируем в BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer

