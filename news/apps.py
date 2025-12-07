from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'
    verbose_name = "📰 СТРАНИЦА 'НОВОСТИ'"
    
    def ready(self):
        """
        Настройка после загрузки приложения.
        """
        # Импортируем сигналы если они есть
        try:
            import news.signals  # noqa: F401
        except ImportError:
            pass