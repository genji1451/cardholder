"""
Административная панель для управления верифицированными картами
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from telegram_bot.models import VerifiedCard, VerificationLog, BotUser, Notification


@admin.register(VerifiedCard)
class VerifiedCardAdmin(admin.ModelAdmin):
    """Админка для верифицированных карт"""
    
    list_display = [
        'id',
        'card_name_display',
        'photo_preview',
        'verification_code_short',
        'is_active',
        'verification_count',
        'created_at',
        'qr_code_link',
    ]
    
    list_filter = [
        'is_active',
        'created_at',
        'updated_at'
    ]
    
    search_fields = [
        'card_name',
        'verification_code',
        'description',
        'owner_info',
        'notes'
    ]
    
    readonly_fields = [
        'verification_code',
        'created_at',
        'updated_at',
        'qr_code_preview',
        'bot_link_display',
        'verification_count',
        'photo_original_preview',
        'photo_packaged_preview'
    ]
    
    fieldsets = (
        ('📝 Основная информация', {
            'fields': (
                'card_name',
                'description',
                'card',
                'is_active',
            ),
            'description': 'Название и описание карты'
        }),
        ('📸 Фотографии', {
            'fields': (
                'photo_original',
                'photo_original_preview',
                'photo_packaged',
                'photo_packaged_preview',
            ),
            'description': 'Фото оригинальной карты и в упаковке'
        }),
        ('🔑 Верификация', {
            'fields': (
                'verification_code',
                'verification_count',
            ),
            'description': 'Код верификации и статистика проверок'
        }),
        ('📊 Статистика', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
        ('📝 Дополнительно', {
            'fields': (
                'owner_info',
                'notes',
            ),
            'classes': ('collapse',)
        }),
        ('🔗 QR-код и ссылки', {
            'fields': (
                'qr_code_preview',
                'bot_link_display',
            ),
            'description': 'QR-код для печати и ссылка для Telegram'
        }),
    )
    
    actions = ['activate_cards', 'deactivate_cards']
    
    def card_name_display(self, obj):
        """Название карты"""
        if obj.card:
            return f"{obj.card.title}"
        return obj.card_name or "Без названия"
    card_name_display.short_description = 'Название'
    card_name_display.admin_order_field = 'card_name'
    
    def photo_preview(self, obj):
        """Миниатюра фото в списке"""
        if obj.photo_original:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.photo_original.url
            )
        return "—"
    photo_preview.short_description = '📸'
    
    def verification_code_short(self, obj):
        """Сокращённый код верификации"""
        return f"{obj.verification_code[:8]}..."
    verification_code_short.short_description = 'Код'
    
    def qr_code_link(self, obj):
        """Ссылка на скачивание QR-кода"""
        return format_html(
            '<a href="/api/telegram-bot/qr-code/{}/download/" target="_blank" '
            'style="background: #0088cc; color: white; padding: 8px 15px; '
            'border-radius: 4px; text-decoration: none; display: inline-block;">📥 Скачать QR</a>',
            obj.id
        )
    qr_code_link.short_description = 'QR'
    
    def bot_link_display(self, obj):
        """Ссылка на бота"""
        bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'cardloginbot')
        link = obj.get_bot_link(bot_username)
        return format_html(
            '<div style="margin-bottom: 10px;">'
            '<a href="{}" target="_blank" style="background: #0088cc; color: white; '
            'padding: 10px 20px; border-radius: 4px; text-decoration: none; display: inline-block;">'
            '🔗 Открыть в Telegram</a>'
            '</div>'
            '<input type="text" value="{}" readonly '
            'style="width: 100%; padding: 8px; border: 1px solid #ddd; '
            'border-radius: 4px; font-family: monospace;" '
            'onclick="this.select(); document.execCommand(\'copy\'); '
            'alert(\'Ссылка скопирована!\');">',
            link, link
        )
    bot_link_display.short_description = 'Ссылка для проверки'
    
    def qr_code_preview(self, obj):
        """Предпросмотр QR-кода"""
        if obj.id:
            return format_html(
                '<div style="text-align: center;">'
                '<img src="/api/telegram-bot/qr-code/{}/" '
                'style="max-width: 300px; border: 1px solid #ddd; border-radius: 8px; padding: 10px;" />'
                '<p style="margin-top: 10px;">Этот QR-код нужно распечатать и наклеить на кейс с картой</p>'
                '</div>',
                obj.id
            )
        return "Сохраните карту, чтобы увидеть QR-код"
    qr_code_preview.short_description = 'QR-код для печати'
    
    def photo_original_preview(self, obj):
        """Превью оригинального фото"""
        if obj.photo_original:
            return format_html(
                '<div style="text-align: center;">'
                '<img src="{}" style="max-width: 400px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />'
                '<p style="margin-top: 10px; color: #666;">Фото карты до упаковки</p>'
                '</div>',
                obj.photo_original.url
            )
        return "Фото не загружено"
    photo_original_preview.short_description = 'Превью оригинала'
    
    def photo_packaged_preview(self, obj):
        """Превью упакованного фото"""
        if obj.photo_packaged:
            return format_html(
                '<div style="text-align: center;">'
                '<img src="{}" style="max-width: 400px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />'
                '<p style="margin-top: 10px; color: #666;">Фото карты в упаковке с QR-кодом</p>'
                '</div>',
                obj.photo_packaged.url
            )
        return "Фото не загружено"
    photo_packaged_preview.short_description = 'Превью упаковки'
    
    def activate_cards(self, request, queryset):
        """Активировать выбранные карты"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'✅ Активировано карт: {updated}', level='success')
    activate_cards.short_description = '✅ Активировать выбранные карты'
    
    def deactivate_cards(self, request, queryset):
        """Деактивировать выбранные карты"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'❌ Деактивировано карт: {updated}', level='warning')
    deactivate_cards.short_description = '❌ Деактивировать выбранные карты'


@admin.register(VerificationLog)
class VerificationLogAdmin(admin.ModelAdmin):
    """Админка для логов верификации"""
    
    list_display = [
        'id',
        'card_info',
        'telegram_user_display',
        'checked_at',
        'ip_address'
    ]
    
    list_filter = [
        'checked_at',
        'verified_card__is_active'
    ]
    
    search_fields = [
        'telegram_user_id',
        'telegram_username',
        'verified_card__card_name',
        'ip_address'
    ]
    
    readonly_fields = [
        'verified_card',
        'verified_card_link',
        'telegram_user_id',
        'telegram_username',
        'checked_at',
        'ip_address',
        'user_agent'
    ]
    
    fieldsets = (
        ('📋 Информация о проверке', {
            'fields': (
                'verified_card',
                'verified_card_link',
                'checked_at',
            )
        }),
        ('👤 Пользователь', {
            'fields': (
                'telegram_user_id',
                'telegram_username',
            )
        }),
        ('🌐 Технические данные', {
            'fields': (
                'ip_address',
                'user_agent',
            ),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'checked_at'
    
    def card_info(self, obj):
        """Информация о карте"""
        if obj.verified_card.card:
            return f"{obj.verified_card.card.title}"
        return obj.verified_card.card_name or "Без названия"
    card_info.short_description = 'Карта'
    card_info.admin_order_field = 'verified_card__card_name'
    
    def verified_card_link(self, obj):
        """Ссылка на верифицированную карту"""
        if obj.verified_card:
            url = reverse('admin:telegram_bot_verifiedcard_change', args=[obj.verified_card.id])
            card_name = obj.verified_card.card_name or "Карта"
            return format_html(
                '<a href="{}" style="background: #0088cc; color: white; padding: 8px 15px; '
                'border-radius: 4px; text-decoration: none; display: inline-block;">🔗 Открыть карту: {}</a>',
                url, card_name
            )
        return "—"
    verified_card_link.short_description = 'Ссылка на карту'
    
    def telegram_user_display(self, obj):
        """Отображение пользователя Telegram"""
        if obj.telegram_username:
            return format_html(
                '<a href="https://t.me/{}" target="_blank">@{}</a> (ID: {})',
                obj.telegram_username, obj.telegram_username, obj.telegram_user_id
            )
        return f"ID: {obj.telegram_user_id}"
    telegram_user_display.short_description = 'Пользователь'
    
    def has_add_permission(self, request):
        """Запрещаем добавление логов вручную"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Запрещаем изменение логов"""
        return False


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    """Админка для пользователей бота"""
    
    list_display = [
        'id',
        'user_display',
        'telegram_id',
        'is_active',
        'is_blocked',
        'interaction_count',
        'last_interaction',
        'first_interaction'
    ]
    
    list_filter = [
        'is_active',
        'is_blocked',
        'is_bot',
        'language_code',
        'first_interaction',
        'last_interaction'
    ]
    
    search_fields = [
        'telegram_id',
        'username',
        'first_name',
        'last_name',
        'notes'
    ]
    
    readonly_fields = [
        'telegram_id',
        'username',
        'first_name',
        'last_name',
        'language_code',
        'is_bot',
        'first_interaction',
        'last_interaction',
        'interaction_count',
        'telegram_link'
    ]
    
    fieldsets = (
        ('👤 Информация о пользователе', {
            'fields': (
                'telegram_id',
                'username',
                'first_name',
                'last_name',
                'telegram_link',
                'language_code',
                'is_bot'
            ),
            'description': 'Основная информация из Telegram'
        }),
        ('📊 Статистика', {
            'fields': (
                'first_interaction',
                'last_interaction',
                'interaction_count',
            )
        }),
        ('⚙️ Настройки', {
            'fields': (
                'is_active',
                'is_blocked',
                'notes',
            )
        }),
    )
    
    date_hierarchy = 'last_interaction'
    actions = ['activate_users', 'deactivate_users', 'send_notification']
    
    def user_display(self, obj):
        """Красивое отображение пользователя"""
        if obj.username:
            return format_html(
                '<strong>@{}</strong><br><small>{}</small>',
                obj.username,
                obj.get_full_name()
            )
        return format_html('<strong>{}</strong>', obj.get_full_name())
    user_display.short_description = 'Пользователь'
    
    def telegram_link(self, obj):
        """Ссылка на пользователя в Telegram"""
        if obj.username:
            return format_html(
                '<a href="https://t.me/{}" target="_blank" '
                'style="background: #0088cc; color: white; padding: 8px 15px; '
                'border-radius: 4px; text-decoration: none; display: inline-block;">'
                '💬 Открыть в Telegram</a>',
                obj.username
            )
        return "Username не указан"
    telegram_link.short_description = 'Telegram'
    
    def activate_users(self, request, queryset):
        """Активировать пользователей"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'✅ Активировано пользователей: {updated}', level='success')
    activate_users.short_description = '✅ Активировать пользователей'
    
    def deactivate_users(self, request, queryset):
        """Деактивировать пользователей"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'❌ Деактивировано пользователей: {updated}', level='warning')
    deactivate_users.short_description = '❌ Деактивировать пользователей'
    
    def send_notification(self, request, queryset):
        """Перенаправить на создание уведомления для выбранных пользователей"""
        user_ids = ','.join(str(u.id) for u in queryset)
        return format_html(
            '<script>window.location.href="/admin/telegram_bot/notification/add/?users={}";</script>',
            user_ids
        )
    send_notification.short_description = '📨 Отправить уведомление'
    
    def has_add_permission(self, request):
        """Запрещаем добавление пользователей вручную"""
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Админка для уведомлений"""
    
    list_display = [
        'id',
        'title',
        'target_type',
        'status',
        'scheduled_for',
        'sent_at',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'target_type',
        'created_at',
        'scheduled_for',
        'sent_at'
    ]
    
    search_fields = [
        'title',
        'message',
        'created_by'
    ]
    
    readonly_fields = [
        'total_recipients',
        'success_count',
        'failed_count',
        'sent_at',
        'created_at',
        'updated_at',
        'error_message',
        'preview_message'
    ]
    
    fieldsets = (
        ('📝 Основная информация', {
            'fields': (
                'title',
                'message',
                'preview_message',
            ),
            'description': 'Название и текст уведомления (HTML поддерживается)'
        }),
        ('🎯 Целевая аудитория', {
            'fields': (
                'target_type',
                'target_user',
            ),
            'description': 'Кому отправить уведомление'
        }),
        ('🖼️ Медиа', {
            'fields': (
                'image',
                'button_text',
                'button_url',
            ),
            'classes': ('collapse',),
            'description': 'Опциональное изображение и кнопка'
        }),
        ('📅 Расписание', {
            'fields': (
                'scheduled_for',
            ),
            'description': 'Оставьте пустым для немедленной отправки'
        }),
        ('📊 Статистика отправки', {
            'fields': (
                'total_recipients',
                'success_count',
                'failed_count',
                'sent_at',
                'error_message',
            ),
            'classes': ('collapse',)
        }),
        ('ℹ️ Дополнительно', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    actions = ['send_notifications', 'duplicate_notification']
    
    def delivery_stats(self, obj):
        """Статистика доставки"""
        if obj.status == 'sent':
            if obj.total_recipients > 0:
                success_rate = (obj.success_count / obj.total_recipients) * 100
                return format_html(
                    '<span style="color: green;">✅ {}/{}</span> '
                    '<span style="color: gray;">({:.1f}%)</span>',
                    obj.success_count, obj.total_recipients, success_rate
                )
            return "✅ Отправлено"
        elif obj.status == 'failed':
            return format_html('<span style="color: red;">❌ Ошибка</span>')
        elif obj.status == 'sending':
            return format_html('<span style="color: orange;">⏳ Отправляется...</span>')
        return "—"
    delivery_stats.short_description = 'Доставка'
    
    def preview_message(self, obj):
        """Превью сообщения"""
        return format_html(
            '<div style="border: 1px solid #ddd; padding: 15px; border-radius: 8px; '
            'background: #f9f9f9; max-width: 600px;">{}</div>',
            obj.message
        )
    preview_message.short_description = 'Превью'
    
    def save_model(self, request, obj, form, change):
        """Сохранение с автозаполнением"""
        if not change:  # Создание нового уведомления
            obj.created_by = request.user.username or request.user.email
            obj.total_recipients = obj.get_recipients_count()
        super().save_model(request, obj, form, change)
    
    def send_notifications(self, request, queryset):
        """Отправить выбранные уведомления"""
        from telegram_bot.tasks import send_notification_task
        
        sent_count = 0
        for notification in queryset.filter(status='draft'):
            try:
                send_notification_task(notification.id)
                sent_count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'❌ Ошибка при отправке "{notification.title}": {e}',
                    level='error'
                )
        
        if sent_count > 0:
            self.message_user(
                request,
                f'✅ Отправлено уведомлений: {sent_count}',
                level='success'
            )
    send_notifications.short_description = '📨 Отправить уведомления'
    
    def duplicate_notification(self, request, queryset):
        """Дублировать уведомление"""
        for notification in queryset:
            notification.pk = None
            notification.status = 'draft'
            notification.sent_at = None
            notification.success_count = 0
            notification.failed_count = 0
            notification.error_message = ''
            notification.title = f"{notification.title} (копия)"
            notification.save()
        
        self.message_user(request, f'✅ Создано копий: {queryset.count()}', level='success')
    duplicate_notification.short_description = '📋 Дублировать уведомление'

