"""
Кастомные настройки админки Django.
"""
from django.contrib import admin
from django.conf import settings


# Получаем оригинальный метод
original_get_app_list = admin.site.__class__.get_app_list


def custom_get_app_list(self, request, app_label=None):
    """
    Переопределяем метод для управления порядком приложений.
    """
    # Получаем стандартный список приложений
    app_list = original_get_app_list(self, request, app_label)
    
    # Если нужен конкретный app_label, возвращаем стандартный список
    if app_label:
        return app_list
    
    # Порядок приложений из настроек
    app_order = getattr(settings, 'ADMIN_APP_ORDER', {})
    
    # Сортируем приложения
    app_list.sort(key=lambda x: app_order.get(x['app_label'], 999))
    
    return app_list


# Применяем кастомную конфигурацию
admin.site.__class__.get_app_list = custom_get_app_list

# Настраиваем заголовки админ-панели
admin.site.site_header = "Панель управления АО «Уголь-Транс»"
admin.site.site_title = "Админ-панель АО «Уголь-Транс»"
admin.site.index_title = "Добро пожаловать в систему управления контентом"