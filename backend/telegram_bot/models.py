"""
Модели для системы верификации карт через Telegram бота
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class VerifiedCard(models.Model):
    """
    Модель для верифицированных карт с QR-кодами
    
    Каждая карта имеет уникальный код верификации, который
    кодируется в QR-коде и используется для проверки подлинности.
    """
    
    # Название карты (вводится админом)
    card_name = models.CharField(
        max_length=255,
        default='',
        blank=True,
        verbose_name='Название карты',
        help_text='Название карты'
    )
    
    # Опциональная связь с каталогом (если есть)
    card = models.ForeignKey(
        'cards.Card',
        on_delete=models.SET_NULL,
        related_name='verifications',
        null=True,
        blank=True,
        verbose_name='Карта из каталога'
    )
    
    verification_code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name='Код верификации',
        help_text='Уникальный код для проверки карты'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна',
        help_text='Можно ли проверить эту карту'
    )
    
    verification_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество проверок',
        help_text='Сколько раз карту проверяли'
    )
    
    # Фото карты (до упаковки - оригинальное)
    photo_original = models.ImageField(
        upload_to='cards/original/',
        null=True,
        blank=True,
        verbose_name='Фото карты (оригинал)',
        help_text='Фото карты до упаковки'
    )
    
    # Фото карты в упаковке (с QR-кодом)
    photo_packaged = models.ImageField(
        upload_to='cards/packaged/',
        null=True,
        blank=True,
        verbose_name='Фото карты в упаковке',
        help_text='Фото карты после упаковки с QR-кодом'
    )
    
    # Описание карты от админа
    description = models.TextField(
        blank=True,
        verbose_name='Описание',
        help_text='Описание карты от администратора'
    )
    
    owner_info = models.TextField(
        blank=True,
        verbose_name='Информация о владельце',
        help_text='Опциональная информация о текущем владельце'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Примечания',
        help_text='Дополнительные заметки о карте'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Верифицированная карта'
        verbose_name_plural = 'Верифицированные карты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['verification_code']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def __str__(self):
        if self.card:
            return f"{self.card.title} - {self.verification_code[:8]}..."
        return f"{self.card_name or 'Карта'} - {self.verification_code[:8]}..."
    
    def save(self, *args, **kwargs):
        """Генерируем уникальный код при создании"""
        if not self.verification_code:
            self.verification_code = self.generate_verification_code()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_verification_code():
        """Генерирует уникальный код верификации"""
        return str(uuid.uuid4())
    
    def get_bot_link(self, bot_username):
        """Возвращает ссылку для проверки карты в боте"""
        return f"https://t.me/{bot_username}?start={self.verification_code}"
    
    def deactivate(self):
        """Деактивирует карту (например, при продаже или утере)"""
        self.is_active = False
        self.save()
    
    def activate(self):
        """Активирует карту"""
        self.is_active = True
        self.save()


class VerificationLog(models.Model):
    """
    Лог проверок карт
    
    Сохраняет историю всех проверок для анализа и безопасности.
    """
    
    verified_card = models.ForeignKey(
        VerifiedCard,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Верифицированная карта'
    )
    
    telegram_user_id = models.BigIntegerField(
        verbose_name='ID пользователя Telegram',
        help_text='ID пользователя, который проверил карту'
    )
    
    telegram_username = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Username Telegram'
    )
    
    checked_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата проверки'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP адрес'
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    
    class Meta:
        verbose_name = 'Лог верификации'
        verbose_name_plural = 'Логи верификаций'
        ordering = ['-checked_at']
        indexes = [
            models.Index(fields=['verified_card', 'checked_at']),
            models.Index(fields=['telegram_user_id', 'checked_at']),
        ]
    
    def __str__(self):
        card_name = self.verified_card.card.title if self.verified_card.card else self.verified_card.card_name
        return f"{card_name} - {self.checked_at.strftime('%d.%m.%Y %H:%M')}"


class BotUser(models.Model):
    """
    Модель пользователя Telegram бота
    
    Автоматически создается при первом взаимодействии пользователя с ботом.
    Используется для рассылки уведомлений и аналитики.
    """
    
    telegram_id = models.BigIntegerField(
        unique=True,
        db_index=True,
        verbose_name='Telegram ID',
        help_text='Уникальный ID пользователя в Telegram'
    )
    
    username = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Username',
        help_text='Username пользователя в Telegram (@username)'
    )
    
    first_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Имя',
        help_text='Имя пользователя'
    )
    
    last_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Фамилия',
        help_text='Фамилия пользователя'
    )
    
    language_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Язык',
        help_text='Код языка пользователя (ru, en, etc.)'
    )
    
    is_bot = models.BooleanField(
        default=False,
        verbose_name='Это бот?'
    )
    
    is_blocked = models.BooleanField(
        default=False,
        verbose_name='Заблокирован',
        help_text='Пользователь заблокировал бота'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен',
        help_text='Получает ли пользователь уведомления'
    )
    
    first_interaction = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Первое взаимодействие',
        help_text='Когда пользователь впервые обратился к боту'
    )
    
    last_interaction = models.DateTimeField(
        auto_now=True,
        verbose_name='Последнее взаимодействие',
        help_text='Когда пользователь последний раз взаимодействовал с ботом'
    )
    
    interaction_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество взаимодействий',
        help_text='Сколько раз пользователь использовал бота'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Примечания',
        help_text='Дополнительная информация о пользователе'
    )
    
    class Meta:
        verbose_name = 'Пользователь бота'
        verbose_name_plural = 'Пользователи бота'
        ordering = ['-last_interaction']
        indexes = [
            models.Index(fields=['telegram_id']),
            models.Index(fields=['is_active', 'is_blocked']),
            models.Index(fields=['-last_interaction']),
        ]
    
    def __str__(self):
        if self.username:
            return f"@{self.username} ({self.telegram_id})"
        elif self.first_name:
            full_name = f"{self.first_name} {self.last_name}".strip()
            return f"{full_name} ({self.telegram_id})"
        return f"User {self.telegram_id}"
    
    def get_full_name(self):
        """Возвращает полное имя пользователя"""
        return f"{self.first_name} {self.last_name}".strip() or self.username or f"User {self.telegram_id}"
    
    def increment_interaction(self):
        """Увеличивает счетчик взаимодействий"""
        self.interaction_count += 1
        self.last_interaction = timezone.now()
        self.save(update_fields=['interaction_count', 'last_interaction'])


class Notification(models.Model):
    """
    Модель уведомлений для рассылки пользователям бота
    
    Позволяет отправлять уведомления всем пользователям или конкретному пользователю.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('scheduled', 'Запланировано'),
        ('sending', 'Отправляется'),
        ('sent', 'Отправлено'),
        ('failed', 'Ошибка'),
    ]
    
    TARGET_CHOICES = [
        ('all', 'Все пользователи'),
        ('active', 'Активные пользователи'),
        ('specific', 'Конкретный пользователь'),
    ]
    
    title = models.CharField(
        max_length=255,
        verbose_name='Название',
        help_text='Название уведомления (для внутреннего использования)'
    )
    
    message = models.TextField(
        verbose_name='Сообщение',
        help_text='Текст уведомления (поддерживает HTML)'
    )
    
    target_type = models.CharField(
        max_length=20,
        choices=TARGET_CHOICES,
        default='all',
        verbose_name='Кому отправить',
        help_text='Выберите целевую аудиторию'
    )
    
    target_user = models.ForeignKey(
        BotUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Конкретный пользователь',
        help_text='Если выбран тип "Конкретный пользователь"'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Статус'
    )
    
    image = models.ImageField(
        upload_to='notifications/',
        null=True,
        blank=True,
        verbose_name='Изображение',
        help_text='Опциональное изображение к уведомлению'
    )
    
    button_text = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Текст кнопки',
        help_text='Опциональная кнопка в уведомлении'
    )
    
    button_url = models.URLField(
        blank=True,
        verbose_name='Ссылка кнопки',
        help_text='URL для кнопки'
    )
    
    scheduled_for = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Запланировано на',
        help_text='Когда отправить уведомление (оставьте пустым для немедленной отправки)'
    )
    
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Отправлено',
        help_text='Когда уведомление было отправлено'
    )
    
    total_recipients = models.PositiveIntegerField(
        default=0,
        verbose_name='Всего получателей',
        help_text='Сколько пользователей должны получить уведомление'
    )
    
    success_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Успешно отправлено',
        help_text='Сколько пользователей получили уведомление'
    )
    
    failed_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Не доставлено',
        help_text='Сколько пользователей не получили уведомление'
    )
    
    error_message = models.TextField(
        blank=True,
        verbose_name='Ошибки',
        help_text='Описание ошибок при отправке'
    )
    
    created_by = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Создано',
        help_text='Кто создал уведомление'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_for']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def get_recipients_count(self):
        """Подсчитывает количество получателей"""
        if self.target_type == 'specific' and self.target_user:
            return 1
        elif self.target_type == 'active':
            return BotUser.objects.filter(is_active=True, is_blocked=False).count()
        else:  # all
            return BotUser.objects.filter(is_blocked=False).count()
    
    def mark_as_sent(self):
        """Помечает уведомление как отправленное"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, error_msg=''):
        """Помечает уведомление как неудачное"""
        self.status = 'failed'
        self.error_message = error_msg
        self.save()

