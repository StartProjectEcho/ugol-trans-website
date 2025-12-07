"""
Контекстные процессоры для шаблонов.
"""
from .models import SiteSettings


def site_settings(request):
    """
    Добавляет настройки сайта в контекст всех шаблонов.
    """
    try:
        settings = SiteSettings.objects.get()
    except SiteSettings.DoesNotExist:
        settings = None
    
    return {
        'site_settings': settings,
    }