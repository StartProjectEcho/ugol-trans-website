from django.apps import AppConfig


class MainPageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main_page'
    verbose_name = '🏠 ГЛАВНАЯ СТРАНИЦА'
    
    def ready(self):
        """
        Настройка после загрузки приложения.
        """
        # Импортируем сигналы если они есть
        try:
            import main_page.signals  # noqa: F401
        except ImportError:
            pass