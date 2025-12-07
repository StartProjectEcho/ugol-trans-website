from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone as tz
from datetime import timedelta
from django.utils.translation import gettext_lazy as _

from core.mixins import ApplicationsCRMAccessMixin
from .models import Application


# ==================== КАСТОМНЫЕ ФИЛЬТРЫ ====================

class ApplicationAgeFilter(admin.SimpleListFilter):
    """Фильтр по возрасту заявки."""
    title = 'Возраст заявки'
    parameter_name = 'age'
    
    def lookups(self, request, model_admin):
        return (
            ('today', 'Сегодня'),
            ('yesterday', 'Вчера'),
            ('week', 'Эта неделя'),
            ('old', 'Старше 3 дней'),
            ('very_old', 'Старше 7 дней'),
        )
    
    def queryset(self, request, queryset):
        now = timezone.now()
        
        if self.value() == 'today':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return queryset.filter(created_at__gte=today_start)
        
        elif self.value() == 'yesterday':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday_start = today_start - timedelta(days=1)
            return queryset.filter(
                created_at__gte=yesterday_start,
                created_at__lt=today_start
            )
        
        elif self.value() == 'week':
            week_ago = now - timedelta(days=7)
            return queryset.filter(created_at__gte=week_ago)
        
        elif self.value() == 'old':
            three_days_ago = now - timedelta(days=3)
            return queryset.filter(created_at__lt=three_days_ago)
        
        elif self.value() == 'very_old':
            week_ago = now - timedelta(days=7)
            return queryset.filter(created_at__lt=week_ago)
        
        return queryset


class ApplicationStatusFilter(admin.SimpleListFilter):
    """Фильтр по статусу с иконками."""
    title = 'Статус'
    parameter_name = 'status'
    
    def lookups(self, request, model_admin):
        return (
            ('new', '🟠 Новые'),
            ('in_progress', '🔵 В работе'),
            ('processed', '🟢 Обработанные'),
            ('rejected', '🔴 Отклоненные'),
        )
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


# ==================== КЛАСС ДЛЯ ЗАЯВОК ====================

@admin.register(Application)
class ApplicationAdmin(ApplicationsCRMAccessMixin, admin.ModelAdmin):
    """
    Админка для заявок. Доступна только админам и CRM-менеджерам.
    """
    # ✏️ ПЕРВЫЙ СТОЛБЕЦ - ИЗМЕНИТЬ
    list_display = (
        'edit_link',
        'id_display',
        'name_display',
        'contact_info_display',
        'status_colored',
        'age_display',
        'created_at_formatted',
        'message_preview_display',
    )
    
    list_filter = (
        ApplicationStatusFilter,
        ApplicationAgeFilter,
        'created_at',
    )
    
    search_fields = ('name', 'phone', 'email', 'message', 'manager_comment')
    
    readonly_fields = (
        'created_at',
        'updated_at',
        'processed_at',
        'contact_info_display',
        'age_display_readonly',
        'status_color_display',
    )
    
    list_per_page = 25
    
    fieldsets = (
        ('Информация о клиенте', {
            'fields': ('name', 'phone', 'email', 'message')
        }),
        ('Обработка заявки', {
            'fields': ('status', 'manager_comment', 'processed_at')
        }),
        ('Дополнительная информация', {
            'fields': ('contact_info_display', 'age_display_readonly', 'status_color_display'),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'mark_as_new',
        'mark_in_progress',
        'mark_processed',
        'mark_rejected',
    ]
    
    # ==================== КОЛОНКА "ИЗМЕНИТЬ" ====================
    def edit_link(self, obj):
        """Ссылка на редактирование в виде текста с карандашиком."""
        url = reverse('admin:applications_application_change', args=[obj.id])
        return format_html(
            '<a href="{}" style="text-decoration: none; color: #447e9b;" title="Редактировать">'
            '<span style="font-size: 14px;">✏️</span> Изменить'
            '</a>',
            url
        )
    edit_link.short_description = ''
    edit_link.admin_order_field = 'id'
    
    def id_display(self, obj):
        """Отображение ID заявки БЕЗ ссылки."""
        return f"#{obj.id}"
    id_display.short_description = 'ID'
    id_display.admin_order_field = 'id'
    
    def name_display(self, obj):
        """Имя клиента БЕЗ ссылки."""
        return obj.name
    name_display.short_description = 'Имя клиента'
    name_display.admin_order_field = 'name'
    
    def contact_info_display(self, obj):
        """Отображение контактной информации."""
        return obj.contact_info
    contact_info_display.short_description = 'Контакты'
    
    def status_colored(self, obj):
        """Цветное отображение статуса."""
        color = obj.status_color
        return format_html(
            '<span style="color: {}; font-weight: bold; padding: 3px 8px; '
            'border-radius: 3px; background-color: {}20;">{}</span>',
            color,
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Статус'
    status_colored.admin_order_field = 'status'
    
    def age_display(self, obj):
        """Умное отображение возраста заявки с учетом статуса."""
        return obj.get_age_display()
    age_display.short_description = 'Возраст'
    age_display.admin_order_field = 'created_at'
    
    def age_display_readonly(self, obj):
        """Только для чтения в форме редактирования."""
        return obj.get_age_display()
    age_display_readonly.short_description = 'Возраст заявки'
    
    def created_at_formatted(self, obj):
        """Форматированная дата создания."""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')
    created_at_formatted.short_description = 'Дата создания'
    created_at_formatted.admin_order_field = 'created_at'
    
    def message_preview_display(self, obj):
        """Превью сообщения с тултипом."""
        if obj.message:
            preview = obj.message[:60] + "..." if len(obj.message) > 60 else obj.message
            return format_html(
                '<span title="{}" style="cursor: help;">{}</span>',
                obj.message.replace('"', '&quot;'),
                preview
            )
        return "—"
    message_preview_display.short_description = 'Сообщение'
    
    def status_color_display(self, obj):
        """Отображение цвета статуса (только для просмотра)."""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; '
            'border: 1px solid #ccc; border-radius: 3px;"></div>',
            obj.status_color
        )
    status_color_display.short_description = 'Цвет статуса'
    
    # ==================== МАССОВЫЕ ДЕЙСТВИЯ ====================
    
    def mark_as_new(self, request, queryset):
        """Пометить выбранные заявки как новые."""
        updated = queryset.update(status='new', processed_at=None)
        self.message_user(
            request,
            f'{updated} заявок помечено как "Новые"',
            messages.SUCCESS
        )
    mark_as_new.short_description = "🟠 Пометить как НОВЫЕ"
    
    def mark_in_progress(self, request, queryset):
        """Пометить выбранные заявки как "В работе"."""
        updated = queryset.update(status='in_progress', processed_at=None)
        self.message_user(
            request,
            f'{updated} заявок помечено как "В работе"',
            messages.SUCCESS
        )
    mark_in_progress.short_description = "🔵 Пометить как В РАБОТЕ"
    
    def mark_processed(self, request, queryset):
        """Пометить выбранные заявки как обработанные."""
        updated = queryset.update(status='processed', processed_at=tz.now())
        self.message_user(
            request,
            f'{updated} заявок помечено как "Обработанные"',
            messages.SUCCESS
        )
    mark_processed.short_description = "🟢 Пометить как ОБРАБОТАННЫЕ"
    
    def mark_rejected(self, request, queryset):
        """Пометить выбранные заявки как отклоненные."""
        updated = queryset.update(status='rejected', processed_at=None)
        self.message_user(
            request,
            f'{updated} заявок помечено как "Отклоненные"',
            messages.SUCCESS
        )
    mark_rejected.short_description = "🔴 Пометить как ОТКЛОНЕННЫЕ"
    
    # ==================== ОПТИМИЗАЦИЯ ====================
    
    def get_queryset(self, request):
        """Оптимизированный queryset."""
        return super().get_queryset(request).order_by('-created_at')
    
    def get_list_filter(self, request):
        """
        Динамические фильтры в зависимости от роли.
        """
        role = getattr(request.user, 'role', None)
        
        if role == 'crm_manager':
            # CRM-менеджеры видят только базовые фильтры
            return (ApplicationStatusFilter, ApplicationAgeFilter)
        else:
            # Админы видят все фильтры
            return super().get_list_filter(request)