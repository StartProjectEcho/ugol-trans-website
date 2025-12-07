# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.contrib.admin import display
from django.contrib import messages
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.urls import reverse
import json
from django.utils import timezone
from datetime import timedelta

from core.mixins import AdminOnlyAccessMixin, HistoryAccessMixin
from .models import User


# ==================== КАСТОМИЗАЦИЯ LogEntry ====================

def logentry_str(self):
    """Кастомный __str__ для LogEntry."""
    try:
        if not self.content_type:
            return f"Объект #{self.object_id}"
        
        model_name = self.content_type.name
        
        obj_name = None
        
        if self.object_repr and len(self.object_repr.strip()) > 0:
            obj_name = self.object_repr.strip()
        else:
            try:
                model_class = self.content_type.model_class()
                if model_class:
                    obj = model_class.objects.filter(pk=self.object_id).first()
                    if obj and hasattr(obj, '__str__'):
                        obj_name = str(obj)
            except Exception:
                pass
        
        if obj_name:
            if len(obj_name) > 80:
                obj_name = f"{obj_name[:77]}..."
            return f"{model_name} '{obj_name}' (#{self.object_id})"
        else:
            return f"{model_name} #{self.object_id}"
    
    except Exception:
        return f"Объект #{self.object_id}"


LogEntry.__str__ = logentry_str

# Убираем стандартную регистрацию LogEntry
try:
    admin.site.unregister(LogEntry)
except admin.sites.NotRegistered:
    pass


# ==================== КАСТОМНЫЕ ФИЛЬТРЫ ====================

class LastLoginFilter(admin.SimpleListFilter):
    """Фильтр по активности пользователей."""
    title = 'Активность'
    parameter_name = 'last_login'
    
    def lookups(self, request, model_admin):
        return (
            ('today', 'Был онлайн сегодня'),
            ('week', 'Был онлайн на этой неделе'),
            ('month', 'Был онлайн в этом месяце'),
            ('never', 'Никогда не заходил'),
            ('inactive', 'Не заходил > 1 месяца'),
        )
    
    def queryset(self, request, queryset):
        now = timezone.now()
        
        if self.value() == 'today':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return queryset.filter(last_login__gte=today_start)
        
        elif self.value() == 'week':
            week_ago = now - timedelta(days=7)
            return queryset.filter(last_login__gte=week_ago)
        
        elif self.value() == 'month':
            month_ago = now - timedelta(days=30)
            return queryset.filter(last_login__gte=month_ago)
        
        elif self.value() == 'never':
            return queryset.filter(last_login__isnull=True)
        
        elif self.value() == 'inactive':
            month_ago = now - timedelta(days=30)
            return queryset.filter(
                last_login__lt=month_ago
            ) | queryset.filter(
                last_login__isnull=True,
                date_joined__lt=month_ago
            )
        
        return queryset


# ==================== КЛАСС ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ====================

@admin.register(User)
class UserAdmin(AdminOnlyAccessMixin, BaseUserAdmin):
    """
    Админка для пользователей. Только для администраторов.
    """
    # Форма для смены пароля
    change_password_form = AdminPasswordChangeForm
    
    # ✏️ ПЕРВЫЙ СТОЛБЕЦ - ИЗМЕНИТЬ
    list_display = (
        'edit_link',
        'username_display',
        'email_display', 
        'get_full_name_display',
        'role_formatted', 
        'is_active_display',  # Изменил название метода
        'last_login_display',
        'date_joined_formatted'
    )
    
    list_filter = (
        'role', 
        'is_active', 
        'date_joined',
        LastLoginFilter,
    )
    
    # ПОЛЯ БЕЗ ССЫЛОК
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Персональная информация'), {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        (_('Роль и доступ'), {'fields': ('is_active', 'role')}),
        (_('Системная информация'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_active'),
        }),
    )
    
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    ordering = ('-date_joined',)  # Новые сверху
    readonly_fields = ('last_login', 'date_joined')
    
    # МАССОВЫЕ ДЕЙСТВИЯ
    actions = ['make_active', 'make_inactive']
    
    # ==================== КОЛОНКА "ИЗМЕНИТЬ" ====================
    def edit_link(self, obj):
        """Ссылка на редактирование в виде текста с карандашиком."""
        url = reverse('admin:accounts_user_change', args=[obj.id])
        return format_html(
            '<a href="{}" style="text-decoration: none; color: #447e9b;" title="Редактировать">'
            '<span style="font-size: 14px;">✏️</span> Изменить'
            '</a>',
            url
        )
    edit_link.short_description = ''
    edit_link.admin_order_field = 'id'
    
    def username_display(self, obj):
        """Имя пользователя БЕЗ ссылки."""
        return obj.username
    username_display.short_description = 'Логин'
    username_display.admin_order_field = 'username'
    
    def email_display(self, obj):
        """Email БЕЗ ссылки."""
        return obj.email or "—"
    email_display.short_description = 'Email'
    email_display.admin_order_field = 'email'
    
    def get_full_name_display(self, obj):
        """Полное имя БЕЗ ссылки."""
        return obj.get_full_name() or "—"
    get_full_name_display.short_description = 'Полное имя'
    
    def role_formatted(self, obj):
        """Форматированное отображение роли."""
        return obj.get_role_display_formatted()
    role_formatted.short_description = 'Роль'
    role_formatted.admin_order_field = 'role'
    
    def is_active_display(self, obj):
        """Простая галочка для активности (без boolean=True)."""
        if obj.is_active:
            return "✅"
        else:
            return "❌"
    is_active_display.short_description = 'Активен'
    is_active_display.admin_order_field = 'is_active'
    
    def last_login_display(self, obj):
        """Отображение последнего входа."""
        return obj.get_last_login_display()
    last_login_display.short_description = 'Последний вход'
    last_login_display.admin_order_field = 'last_login'
    
    def date_joined_formatted(self, obj):
        """Форматированная дата регистрации."""
        return obj.date_joined.strftime('%d.%m.%Y')
    date_joined_formatted.short_description = 'Дата регистрации'
    date_joined_formatted.admin_order_field = 'date_joined'
    
    # ==================== МАССОВЫЕ ДЕЙСТВИЯ ====================
    
    def make_active(self, request, queryset):
        """Активировать выбранных пользователей."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, 
            f'Активировано пользователей: {updated}', 
            messages.SUCCESS
        )
    make_active.short_description = "✅ Активировать выбранных"
    
    def make_inactive(self, request, queryset):
        """Деактивировать выбранных пользователей."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, 
            f'Деактивировано пользователей: {updated}', 
            messages.SUCCESS
        )
    make_inactive.short_description = "❌ Деактивировать выбранных"


# ==================== ИСТОРИЯ ДЕЙСТВИЙ ====================

@admin.register(LogEntry)
class CustomLogEntryAdmin(HistoryAccessMixin, admin.ModelAdmin):
    """
    Админка для истории действий. Только для администраторов.
    """
    # ✏️ ПЕРВЫЙ СТОЛБЕЦ - ПОДРОБНЕЕ
    list_display = (
        'view_details_link',
        'action_time_formatted', 
        'user_display', 
        'action_description', 
        'object_display',
    )
    
    list_per_page = 50
    list_filter = ('action_time', 'user', 'content_type', 'action_flag')
    search_fields = ('object_repr', 'user__username', 'change_message')
    date_hierarchy = 'action_time'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            logentry_content_type = ContentType.objects.get_for_model(LogEntry)
            qs = qs.exclude(content_type=logentry_content_type)
        except ContentType.DoesNotExist:
            pass
        return qs.select_related('user', 'content_type')
    
    def view_details_link(self, obj):
        """Ссылка на просмотр деталей."""
        url = reverse('admin:admin_logentry_change', args=[obj.id])
        return format_html(
            '<a href="{}" style="text-decoration: none; color: #447e9b;" title="Подробнее">'
            '<span style="font-size: 14px;">🔍</span> Подробнее'
            '</a>',
            url
        )
    view_details_link.short_description = ''
    
    def action_time_formatted(self, obj): 
        return obj.action_time.strftime('%d.%m.%Y %H:%M:%S')
    action_time_formatted.short_description = 'Дата и время'
    action_time_formatted.admin_order_field = 'action_time'
    
    def user_display(self, obj):
        """Пользователь БЕЗ ссылки."""
        return obj.user.username if obj.user else "—"
    user_display.short_description = 'Пользователь'
    
    def action_description(self, obj):
        if obj.action_flag == ADDITION:
            return "Создание"
        elif obj.action_flag == CHANGE:
            return "Изменение"
        elif obj.action_flag == DELETION:
            return "Удаление"
        return "Неизвестное действие"
    action_description.short_description = 'Тип действия'
    
    def object_display(self, obj):
        display_text = str(obj)
        
        if obj.action_flag == DELETION:
            return f"{display_text} (удален)"
        
        return display_text
    object_display.short_description = 'Объект'
    
    def change_message_formatted(self, obj):
        if not obj.change_message:
            return "Нет информации об изменениях"
        
        try:
            changes = json.loads(obj.change_message)
            if isinstance(changes, list) and changes:
                result = []
                for change in changes:
                    if isinstance(change, dict):
                        for key in ['changed', 'added', 'deleted']:
                            if key in change:
                                name = change[key].get('name', '')
                                if key == 'changed':
                                    fields = change[key].get('fields', [])
                                    if fields:
                                        result.append(f"В объекте {name} изменены поля: {', '.join(fields)}")
                                    else:
                                        result.append(f"Объект {name} изменен")
                                else:
                                    result.append(f"Объект {name} {self._get_action_verb(key)}")
                
                if result:
                    return format_html('<br>'.join(result))
            
            return format_html('<pre style="white-space: pre-wrap;">{}</pre>', 
                             json.dumps(changes, ensure_ascii=False, indent=2))
            
        except (json.JSONDecodeError, TypeError):
            return format_html('<pre style="white-space: pre-wrap;">{}</pre>', str(obj.change_message))
    
    def _get_action_verb(self, key):
        verbs = {
            'added': 'добавлен',
            'deleted': 'удален'
        }
        return verbs.get(key, 'обработан')
    
    change_message_formatted.short_description = 'Подробности изменений'
    
    def action_time_formatted_field(self, obj):
        return obj.action_time.strftime('%d.%m.%Y %H:%M:%S')
    action_time_formatted_field.short_description = 'Дата и время'
    
    def action_flag_formatted(self, obj):
        if obj.action_flag == ADDITION:
            return "Создание"
        elif obj.action_flag == CHANGE:
            return "Изменение"
        elif obj.action_flag == DELETION:
            return "Удаление"
        return f"Неизвестное действие ({obj.action_flag})"
    action_flag_formatted.short_description = 'Тип действия'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('action_time_formatted_field', 'user_display', 'content_type', 'action_flag_formatted')
        }),
        ('Объект', {
            'fields': ('object_repr', 'object_id')
        }),
        ('Изменения', {
            'fields': ('change_message_formatted',)
        }),
    )
    
    readonly_fields = ('action_time_formatted_field', 'user_display', 'content_type', 
                      'action_flag_formatted', 'object_repr', 'object_id', 
                      'change_message_formatted')
    
    # Отключаем редактирование
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

    def render_change_form(self, request, context, *args, **kwargs):
        has_delete_perm = super().has_delete_permission(request, kwargs.get('obj'))
        
        context.update({
            'show_save': False,
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
            'show_delete': has_delete_perm,
            'title': 'Просмотр записи истории действий',
        })
        return super().render_change_form(request, context, *args, **kwargs)