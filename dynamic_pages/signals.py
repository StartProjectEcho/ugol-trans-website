from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_default_pages_and_sections(sender, **kwargs):
    """Автоматически создает страницы и базовые секции"""
    if sender.name == 'dynamic_pages':
        print("\n" + "="*60)
        print("СОЗДАНИЕ ДИНАМИЧЕСКИХ СТРАНИЦ И СЕКЦИЙ")
        print("="*60)
        
        try:
            from .models import (
                AboutPage, ServicesPage, DocumentsPage,
                AboutSection, ServiceSection, DocumentSection
            )
            
            # 1. Создаем синглтон-страницы
            about_page, about_created = AboutPage.objects.get_or_create(
                pk=1,
                defaults={
                    'title': 'О компании АО «Уголь-Транс»',
                    'meta_description': '25 лет на рынке железнодорожных перевозок. История, миссия и ценности компании.'
                }
            )
            
            services_page, services_created = ServicesPage.objects.get_or_create(
                pk=1,
                defaults={
                    'title': 'Услуги АО «Уголь-Транс»',
                    'meta_description': 'Железнодорожные перевозки угля, логистические решения, комплексные транспортные услуги.'
                }
            )
            
            documents_page, documents_created = DocumentsPage.objects.get_or_create(
                pk=1,
                defaults={
                    'title': 'Документы АО «Уголь-Транс»',
                    'meta_description': 'Лицензии, сертификаты, нормативные документы компании.'
                }
            )
            
            print("✅ Созданы страницы:")
            print(f"   • {about_page}")
            print(f"   • {services_page}")
            print(f"   • {documents_page}")
            
            # 2. Создаем секции для "О компании"
            about_sections = [
                {
                    'about_page': about_page,
                    'menu_title': 'История компании',
                    'title': 'История АО «Уголь-Транс»',
                    'subtitle': '25 лет на рынке железнодорожных перевозок',
                    'content': 'Основана в 1998 году как специализированный оператор угольных перевозок. Начав с парка в 500 вагонов, сегодня компания располагает более 15,000 единиц подвижного состава.',
                    'layout': 'layout_1',
                    'order': 1,
                    'is_active': True
                },
                {
                    'about_page': about_page,
                    'menu_title': 'Миссия и ценности',
                    'title': 'Наша миссия и корпоративные ценности',
                    'subtitle': 'Современные решения для традиционных отраслей',
                    'content': 'Миссия компании: обеспечение надежных и эффективных логистических решений для угольной промышленности России. Ценности: безопасность, надежность, инновации, социальная ответственность.',
                    'layout': 'layout_2',
                    'order': 2,
                    'is_active': True
                },
                {
                    'about_page': about_page,
                    'menu_title': 'Руководство',
                    'title': 'Руководство компании',
                    'subtitle': 'Опытная команда управленцев',
                    'content': 'Генеральный директор - Иванов Иван Иванович (опыт в отрасли 20 лет). Технический директор - Петров Петр Петрович (опыт 15 лет).',
                    'layout': 'layout_3',
                    'order': 3,
                    'is_active': True
                },
            ]
            
            for section_data in about_sections:
                AboutSection.objects.update_or_create(
                    about_page=about_page,
                    menu_title=section_data['menu_title'],
                    defaults=section_data
                )
            print(f"✅ Созданы секции для 'О компании': {len(about_sections)} секций")
            
            # 3. Создаем секции для "Услуги"
            service_sections = [
                {
                    'services_page': services_page,
                    'menu_title': 'Железнодорожные перевозки',
                    'title': 'Железнодорожные грузоперевозки',
                    'subtitle': 'Полный цикл транспортно-логистических услуг',
                    'content': 'Организация перевозок угля, кокса и сырьевых грузов по всей России. Ежегодный объем перевозок - более 50 млн тонн.',
                    'layout': 'layout_1',
                    'order': 1,
                    'is_active': True
                },
                {
                    'services_page': services_page,
                    'menu_title': 'Логистические решения',
                    'title': 'Комплексные логистические решения',
                    'subtitle': 'От планирования до доставки',
                    'content': 'Разработка индивидуальных логистических схем, оптимизация маршрутов, складская логистика, экспедирование грузов.',
                    'layout': 'layout_2',
                    'order': 2,
                    'is_active': True
                },
                {
                    'services_page': services_page,
                    'menu_title': 'Консультационные услуги',
                    'title': 'Консультационные услуги',
                    'subtitle': 'Экспертиза в области логистики',
                    'content': 'Консультации по вопросам железнодорожных перевозок, таможенного оформления, оптимизации логистических цепочек.',
                    'layout': 'layout_4',
                    'order': 3,
                    'is_active': True
                },
            ]
            
            for section_data in service_sections:
                ServiceSection.objects.update_or_create(
                    services_page=services_page,
                    menu_title=section_data['menu_title'],
                    defaults=section_data
                )
            print(f"✅ Созданы секции для 'Услуги': {len(service_sections)} секций")
            
            # 4. Создаем секции для "Документы"
            document_sections = [
                {
                    'documents_page': documents_page,
                    'menu_title': 'Лицензии и сертификаты',
                    'title': 'Лицензии и сертификаты компании',
                    'subtitle': 'Документы, подтверждающие нашу деятельность',
                    'content': 'Лицензия на осуществление перевозок железнодорожным транспортом. Сертификаты соответствия системы менеджмента качества.',
                    'layout': 'layout_1',
                    'order': 1,
                    'is_active': True
                },
                {
                    'documents_page': documents_page,
                    'menu_title': 'Финансовая отчетность',
                    'title': 'Финансовая отчетность',
                    'subtitle': 'Прозрачность и открытость',
                    'content': 'Годовая бухгалтерская отчетность, аудиторские заключения, отчеты о финансовых результатах.',
                    'layout': 'layout_3',
                    'order': 2,
                    'is_active': True
                },
            ]
            
            for section_data in document_sections:
                DocumentSection.objects.update_or_create(
                    documents_page=documents_page,
                    menu_title=section_data['menu_title'],
                    defaults=section_data
                )
            print(f"✅ Созданы секции для 'Документы': {len(document_sections)} секций")
            
            print("="*60)
            print("ВСЕ ДИНАМИЧЕСКИЕ СТРАНИЦЫ И СЕКЦИИ УСПЕШНО СОЗДАНЫ!")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"❌ ОШИБКА при создании страниц и секций: {e}")
            import traceback
            traceback.print_exc()