"""
Тесты для Telegram Bot
"""

from django.test import TestCase
from django.contrib.auth.models import User
from apps.cards.models import Card, Series
from telegram_bot.models import VerifiedCard, VerificationLog
from telegram_bot.utils import generate_qr_code, format_card_info


class VerifiedCardModelTest(TestCase):
    """Тесты модели VerifiedCard"""
    
    def setUp(self):
        """Создаём тестовые данные"""
        self.series = Series.objects.create(number=1, title="Test Series")
        self.card = Card.objects.create(
            title="Test Card",
            number=1,
            rarity="о",
            series=self.series,
            base_price_rub=100
        )
    
    def test_verified_card_creation(self):
        """Тест создания верифицированной карты"""
        verified_card = VerifiedCard.objects.create(card=self.card)
        
        # Проверяем, что код верификации сгенерирован автоматически
        self.assertIsNotNone(verified_card.verification_code)
        self.assertTrue(len(verified_card.verification_code) > 0)
        
        # Проверяем значения по умолчанию
        self.assertTrue(verified_card.is_active)
        self.assertEqual(verified_card.verification_count, 0)
    
    def test_verification_code_unique(self):
        """Тест уникальности кода верификации"""
        card1 = VerifiedCard.objects.create(card=self.card)
        
        card2 = Card.objects.create(
            title="Test Card 2",
            number=2,
            rarity="о",
            series=self.series
        )
        verified_card2 = VerifiedCard.objects.create(card=card2)
        
        # Коды должны быть разными
        self.assertNotEqual(card1.verification_code, verified_card2.verification_code)
    
    def test_get_bot_link(self):
        """Тест генерации ссылки на бота"""
        verified_card = VerifiedCard.objects.create(card=self.card)
        bot_username = "test_bot"
        
        link = verified_card.get_bot_link(bot_username)
        
        self.assertIn(bot_username, link)
        self.assertIn(verified_card.verification_code, link)
        self.assertTrue(link.startswith("https://t.me/"))
    
    def test_activate_deactivate(self):
        """Тест активации/деактивации карты"""
        verified_card = VerifiedCard.objects.create(card=self.card)
        
        # Карта активна по умолчанию
        self.assertTrue(verified_card.is_active)
        
        # Деактивируем
        verified_card.deactivate()
        self.assertFalse(verified_card.is_active)
        
        # Активируем обратно
        verified_card.activate()
        self.assertTrue(verified_card.is_active)


class VerificationLogModelTest(TestCase):
    """Тесты модели VerificationLog"""
    
    def setUp(self):
        """Создаём тестовые данные"""
        self.series = Series.objects.create(number=1, title="Test Series")
        self.card = Card.objects.create(
            title="Test Card",
            number=1,
            rarity="о",
            series=self.series
        )
        self.verified_card = VerifiedCard.objects.create(card=self.card)
    
    def test_log_creation(self):
        """Тест создания лога"""
        log = VerificationLog.objects.create(
            verified_card=self.verified_card,
            telegram_user_id=123456789,
            telegram_username="test_user"
        )
        
        self.assertEqual(log.verified_card, self.verified_card)
        self.assertEqual(log.telegram_user_id, 123456789)
        self.assertEqual(log.telegram_username, "test_user")
        self.assertIsNotNone(log.checked_at)


class UtilsTest(TestCase):
    """Тесты утилит"""
    
    def setUp(self):
        """Создаём тестовые данные"""
        self.series = Series.objects.create(number=1, title="Test Series")
        self.card = Card.objects.create(
            title="Spider-Man",
            number=1,
            rarity="ук",
            series=self.series,
            base_price_rub=500
        )
        self.verified_card = VerifiedCard.objects.create(card=self.card)
    
    def test_generate_qr_code(self):
        """Тест генерации QR-кода"""
        qr_buffer = generate_qr_code("https://test.com")
        
        # Проверяем, что получили BytesIO объект
        self.assertIsNotNone(qr_buffer)
        
        # Проверяем, что размер не нулевой
        qr_buffer.seek(0, 2)  # Перемещаемся в конец
        size = qr_buffer.tell()
        self.assertGreater(size, 0)
    
    def test_format_card_info(self):
        """Тест форматирования информации о карте"""
        info = format_card_info(self.card, self.verified_card)
        
        # Проверяем, что информация содержит ключевые данные
        self.assertIn("Spider-Man", info)
        self.assertIn("#1", info)
        self.assertIn("Test Series", info)
        self.assertIn("ОРИГИНАЛЬНАЯ КАРТА", info)

