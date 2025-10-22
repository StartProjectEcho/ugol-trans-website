# 🏗️ Архитектура проекта АО "Уголь-Транс"

## 📁 Структура проекта

ugol_trans/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
├── architecture.md
├── README.md
├── ugol_trans_site/ # Основная конфигурация проекта
│ ├── init.py
│ ├── settings.py
│ ├── urls.py
│ ├── wsgi.py
│ └── celery.py
├── core/ # Базовые модели и утилиты
│ ├── init.py
│ ├── admin.py
│ ├── apps.py
│ ├── models.py
│ ├── tests.py
│ └── views.py
├── main/ # Главная страница и контент
│ ├── init.py
│ ├── admin.py
│ ├── apps.py
│ ├── models.py
│ ├── tests.py
│ └── views.py
├── analytics/ # Бизнес-аналитика
│ ├── init.py
│ ├── admin.py
│ ├── apps.py
│ ├── models.py
│ ├── tests.py
│ └── views.py
├── news/ # Новостная система
│ ├── init.py
│ ├── admin.py
│ ├── apps.py
│ ├── models.py
│ ├── tests.py
│ └── views.py
├── contacts/ # Обратная связь и контакты
│ ├── init.py
│ ├── admin.py
│ ├── apps.py
│ ├── models.py
│ ├── tests.py
│ └── views.py
├── config/ # Настройки сайта
│ ├── init.py
│ ├── admin.py
│ ├── apps.py
│ ├── models.py
│ ├── tests.py
│ └── views.py
└── templates/ # Шаблоны
├── base.html
├── main/
├── news/
├── contacts/
└── includes/


## 🗄️ Модели данных по приложениям

### core (3 модели)
- TimeStampedModel (abstract)
- SoftDeleteModel (abstract) 
- UserStampedModel (abstract)
- MediaLibrary

### main (8 моделей)
- HeroSection
- AboutSection
- Advantage
- AnalyticsSection
- Partner
- CTASection
- PageContent
- PageMedia

### analytics (4 модели)
- AnalyticsYear
- CargoCategory
- CargoSubCategory
- CargoData

### news (3 модели)
- NewsCategory
- Tag
- News

### contacts (3 модели)
- Application
- CompanyContact
- SocialNetwork

### config (6 моделей)
- SEOSettings
- SiteConfig
- Menu
- Redirect
- BackupLog
- UserProfile
- FAQ

## 🔗 Зависимости между приложениями

core (базовые модели)
↓
main (главная страница) → news (новости) → analytics (данные)
↓
contacts (формы) → config (настройки)


## ⚙️ Технологический стек

### Бэкенд
- Django 4.2.8
- PostgreSQL 15+
- Redis 7+
- Celery
- Django CKEditor

### Фронтенд
- HTML5, CSS3, Bootstrap 5.3
- JavaScript (Vanilla JS + jQuery)
- Chart.js, Leaflet

### Инфраструктура
- Gunicorn + Nginx
- Whitenoise для статики
- Sentry для мониторинга