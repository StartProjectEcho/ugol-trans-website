import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Безопасный ключ с fallback для разработки
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Только разработка
DEBUG = True

# Локальные хосты для разработки
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Приложения проекта
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Сторонние библиотеки
    'solo',
    'adminsortable2',
    'nested_admin',
    'django_cleanup',
    
    # Кастомные приложения
    'core',
    'accounts',
    'news',
    'main_page',
    'dynamic_pages',
    'contacts',
    'applications',
    'business_analytics',
]

# Промежуточное ПО
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ugol_trans_site.urls'

# Настройки шаблонов
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'ugol_trans_site.wsgi.application'

# База данных PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'ugol_trans_dev'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Валидаторы паролей
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Локализация
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Статические файлы
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Медиафайлы
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Поле по умолчанию для моделей
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Кастомная модель пользователя
AUTH_USER_MODEL = 'accounts.User'

# Бэкенды аутентификации
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Email настройки
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'true').lower() == 'true'
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'false').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER

# Дополнительные настройки SMTP
EMAIL_TIMEOUT = 30
EMAIL_SSL_KEYFILE = None
EMAIL_SSL_CERTFILE = None

# Количество элементов на странице в админке
ADMIN_ITEMS_PER_PAGE = 50

# Настройки логирования
from core.logging_config import LOGGING_DICT
LOGGING = LOGGING_DICT

# Настройки сессий для разработки
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 недели
SESSION_SAVE_EVERY_REQUEST = True

# Кэш в памяти для разработки
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Ограничения файлов для разработки
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']

# Порядок приложений в админке
ADMIN_APP_ORDER = {
    'main_page': 1,
    'news': 2,
    'dynamic_pages': 3,
    'contacts': 4,
    'business_analytics': 5,
    'applications': 6,
    'accounts': 7,
    'core': 8,
}

# Показать стандартные модели Django
SHOW_DEFAULT_MODELS = False

# Директория для логов
LOG_DIR = BASE_DIR / 'logs'

# Настройки социальных сетей
SOCIAL_MEDIA_SETTINGS = {
    'ICON_WIDTH': 48,
    'ICON_HEIGHT': 48,
    'MAX_ICON_SIZE': 2 * 1024 * 1024,
    'ALLOWED_ICON_EXTENSIONS': ['.png', '.jpg', '.jpeg', '.svg', '.webp'],
}

# Настройки телефонов
PHONE_VALIDATION = {
    'MIN_DIGITS': 10,
    'FORMATS': ['+7 XXX XXX-XX-XX', '8 XXX XXX-XX-XX'],
}