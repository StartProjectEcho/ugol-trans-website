"""
Миксины для контроля доступа в админке Django.
Используются для разделения прав по ролям пользователей.
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class BaseAccessMixin:
    """
    Базовый миксин для проверки доступа.
    """
    
    def get_user_role(self, request):
        """
        Получает роль пользователя.
        
        Args:
            request: HttpRequest объект
            
        Returns:
            str или None: Роль пользователя или None если нет доступа
        """
        if not request.user.is_authenticated or not request.user.is_staff:
            return None
        
        role = getattr(request.user, 'role', None)
        
        # Логируем вход в админку (только для отладки)
        logger.debug(
            f"Admin access: User={request.user.username}, "
            f"Role={role}, Model={self.__class__.__name__}"
        )
        
        return role
    
    def _has_role_permission(self, request, allowed_roles):
        """
        Вспомогательный метод для проверки ролей.
        
        Args:
            request: HttpRequest объект
            allowed_roles: Список разрешенных ролей
            
        Returns:
            bool: True если доступ разрешен
        """
        role = self.get_user_role(request)
        return role in allowed_roles if role else False


class AdminOnlyAccessMixin(BaseAccessMixin):
    """
    ТОЛЬКО для администраторов.
    Используется для: Пользователи, История действий.
    """
    
    def has_module_permission(self, request):
        return self._has_role_permission(request, ['admin'])
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_add_permission(self, request):
        return self.has_module_permission(request)
    
    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)


class ContentManagerAccessMixin(BaseAccessMixin):
    """
    Для контент-менеджеров и администраторов.
    Используется для: главная страница, страницы, бизнес-аналитика, 
                     изображения, файлы, новости, контакты.
    """
    
    def has_module_permission(self, request):
        return self._has_role_permission(request, ['admin', 'content_manager'])
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_add_permission(self, request):
        return self.has_module_permission(request)
    
    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)


class ApplicationsCRMAccessMixin(BaseAccessMixin):
    """
    ТОЛЬКО для заявок: CRUD для CRM-менеджеров и администраторов.
    """
    
    def has_module_permission(self, request):
        return self._has_role_permission(request, ['admin', 'crm_manager'])
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_add_permission(self, request):
        return self.has_module_permission(request)
    
    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)


class InlineAccessMixin:
    """
    Миксин для inline форм, наследует права от родительского админа.
    """
    
    def get_parent_admin(self):
        """
        Получает родительский admin класс.
        
        Returns:
            ModelAdmin или None: Родительский админ
        """
        from django.contrib import admin
        model_admin = admin.site._registry.get(self.parent_model)
        return model_admin
    
    def has_add_permission(self, request, obj=None):
        parent_admin = self.get_parent_admin()
        if parent_admin and hasattr(parent_admin, 'has_add_permission'):
            return parent_admin.has_add_permission(request)
        return super().has_add_permission(request, obj)
    
    def has_change_permission(self, request, obj=None):
        parent_admin = self.get_parent_admin()
        if parent_admin and hasattr(parent_admin, 'has_change_permission'):
            return parent_admin.has_change_permission(request, obj)
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        parent_admin = self.get_parent_admin()
        if parent_admin and hasattr(parent_admin, 'has_delete_permission'):
            return parent_admin.has_delete_permission(request, obj)
        return super().has_delete_permission(request, obj)


class SiteSettingsAccessMixin(BaseAccessMixin):
    """
    Специальный миксин для SiteSettings с разными правами доступа.
    """
    
    def has_module_permission(self, request):
        return self._has_role_permission(request, ['admin', 'content_manager'])
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_add_permission(self, request):
        # SiteSettings - синглтон, нельзя добавлять
        return False
    
    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        # SiteSettings - синглтон, нельзя удалять
        return False
    
    def get_fieldsets(self, request, obj=None):
        """
        Разные fieldsets для разных ролей.
        
        Args:
            request: HttpRequest объект
            obj: Объект модели
            
        Returns:
            tuple: Кортеж с fieldsets
        """
        role = self.get_user_role(request)
        
        if role == 'admin':
            # Админ видит всё
            return (
                ('Основные настройки', {
                    'fields': ('site_name', 'company_full_name', 'logo', 'favicon')
                }),
                ('Уведомления', {
                    'fields': ('notification_emails', 'default_email_from')
                }),
                ('Интеграции', {
                    'fields': ('recaptcha_site_key', 'recaptcha_secret_key', 'yandex_metrica_id')
                }),
            )
        elif role == 'content_manager':
            # Контент-менеджер видит только основные настройки
            return (
                ('Основные настройки', {
                    'fields': ('site_name', 'company_full_name', 'logo', 'favicon')
                }),
            )
        return super().get_fieldsets(request, obj)
    
    def get_readonly_fields(self, request, obj=None):
        """
        Разные readonly поля для разных ролей.
        
        Args:
            request: HttpRequest объект
            obj: Объект модели
            
        Returns:
            list: Список readonly полей
        """
        role = self.get_user_role(request)
        
        if role == 'content_manager':
            # Контент-менеджер не может менять email и ключи
            return [
                'notification_emails',
                'default_email_from',
                'recaptcha_site_key', 
                'recaptcha_secret_key',
                'yandex_metrica_id'
            ]
        return super().get_readonly_fields(request, obj)


class HistoryAccessMixin(BaseAccessMixin):
    """
    Доступ к истории действий:
    - Админ: видит ВСЕ действия всех пользователей
    - Контент-менеджер: НЕ ВИДИТ историю
    - CRM-менеджер: НЕ ВИДИТ историю
    """
    
    def has_module_permission(self, request):
        return self._has_role_permission(request, ['admin'])
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Только админ может удалять записи истории
        return self.has_module_permission(request)


# ==================== ДЕКОРАТОРЫ ДЛЯ VIEWS ====================
# (Дополнительные утилиты для контроля доступа во views)

from django.contrib.auth.decorators import user_passes_test


def admin_required(view_func=None, login_url=None):
    """
    Декоратор для views, требующий роли администратора.
    
    Usage:
        @admin_required
        def my_view(request):
            ...
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff and getattr(u, 'role', None) == 'admin',
        login_url=login_url
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def content_manager_required(view_func=None, login_url=None):
    """
    Декоратор для views, требующий роли контент-менеджера или администратора.
    
    Usage:
        @content_manager_required
        def my_view(request):
            ...
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff and getattr(u, 'role', None) in ['admin', 'content_manager'],
        login_url=login_url
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def crm_manager_required(view_func=None, login_url=None):
    """
    Декоратор для views, требующий роли CRM-менеджера или администратора.
    
    Usage:
        @crm_manager_required
        def my_view(request):
            ...
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff and getattr(u, 'role', None) in ['admin', 'crm_manager'],
        login_url=login_url
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def staff_required(view_func=None, login_url=None):
    """
    Декоратор для views, требующий любой роли сотрудника (is_staff=True).
    
    Usage:
        @staff_required
        def my_view(request):
            ...
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url=login_url
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


# ==================== КЛАССЫ ДЛЯ CBV ====================

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class AdminRequiredMixin(UserPassesTestMixin):
    """
    Миксин для Class-Based Views, требующий роли администратора.
    
    Usage:
        class MyView(AdminRequiredMixin, View):
            ...
    """
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_staff and getattr(user, 'role', None) == 'admin'
    
    def handle_no_permission(self):
        raise PermissionDenied("Доступ разрешен только администраторам.")


class ContentManagerRequiredMixin(UserPassesTestMixin):
    """
    Миксин для Class-Based Views, требующий роли контент-менеджера или администратора.
    
    Usage:
        class MyView(ContentManagerRequiredMixin, View):
            ...
    """
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_staff and getattr(user, 'role', None) in ['admin', 'content_manager']
    
    def handle_no_permission(self):
        raise PermissionDenied("Доступ разрешен только контент-менеджерам и администраторам.")


class CRMRequiredMixin(UserPassesTestMixin):
    """
    Миксин для Class-Based Views, требующий роли CRM-менеджера или администратора.
    
    Usage:
        class MyView(CRMRequiredMixin, View):
            ...
    """
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_staff and getattr(user, 'role', None) in ['admin', 'crm_manager']
    
    def handle_no_permission(self):
        raise PermissionDenied("Доступ разрешен только CRM-менеджерам и администраторам.")


class StaffRequiredMixin(UserPassesTestMixin):
    """
    Миксин для Class-Based Views, требующий любой роли сотрудника.
    
    Usage:
        class MyView(StaffRequiredMixin, View):
            ...
    """
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_staff
    
    def handle_no_permission(self):
        raise PermissionDenied("Доступ разрешен только сотрудникам компании.")