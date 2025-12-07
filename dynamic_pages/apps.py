from django.apps import AppConfig


class DynamicPagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dynamic_pages'
    verbose_name = '📄 ДИНАМИЧЕСКИЕ СТРАНИЦЫ'
    
    def ready(self):
        # Импортируем сигналы для создания тестовых данных
        try:
            import dynamic_pages.signals
        except ImportError:
            pass