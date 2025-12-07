"""
Конфигурация приложения core.
"""
from django.apps import AppConfig
from django.conf import settings 


class CoreConfig(AppConfig):
    """
    Конфигурация приложения core.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = '⚙️ ОБЩИЕ НАСТРОЙКИ'
    
    def ready(self):
        """
        Инициализация приложения.
        """
        self.setup_admin()
        
        # Импортируем сигналы
        import core.signals  # noqa: F401
    
    def setup_admin(self):
        """
        Настройка админки.
        """
        from django.contrib import admin
        from django.contrib.auth.models import Group, Permission
        
        # Скрываем стандартные модели если нужно
        if not getattr(settings, 'SHOW_DEFAULT_MODELS', False):
            try:
                admin.site.unregister(Group)
            except admin.sites.NotRegistered:
                pass
            
            try:
                admin.site.unregister(Permission)
            except admin.sites.NotRegistered:
                pass