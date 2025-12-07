"""
Конфигурация логирования для проекта.
"""
import os
from pathlib import Path
from django.conf import settings

# Базовый путь для логов из настроек или по умолчанию
BASE_DIR = getattr(settings, 'BASE_DIR', Path(__file__).resolve().parent.parent.parent)
LOG_DIR = getattr(settings, 'LOG_DIR', BASE_DIR / 'logs')

# Создаем директорию для логов если её нет
LOG_DIR.mkdir(exist_ok=True)

# Пути к файлам логов
GENERAL_LOG_PATH = str(LOG_DIR / 'general.log')
ERRORS_LOG_PATH = str(LOG_DIR / 'errors.log')
ADMIN_LOG_PATH = str(LOG_DIR / 'admin.log')
APPLICATIONS_LOG_PATH = str(LOG_DIR / 'applications.log')

LOGGING_DICT = {
    'version': 1,
    'disable_existing_loggers': False,
    
    'formatters': {
        'simple': {
            'format': '{levelname} {asctime} {name}: {message}',
            'style': '{',
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file_general': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': GENERAL_LOG_PATH,
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
            'formatter': 'simple',
        },
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': ERRORS_LOG_PATH,
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    
    'loggers': {
        'django': {
            'handlers': ['console', 'file_general', 'file_errors'],
            'level': 'INFO',
            'propagate': True,
        },
        'core': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },
        'applications': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}