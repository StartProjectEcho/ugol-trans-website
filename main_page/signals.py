# main_page/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_main_page_blocks(sender, **kwargs):
    """Автоматически создает singleton-блоки при миграциях"""
    if sender.name == 'main_page':
        from .models import (
            HeroBlock, AboutBlock, AdvantageBlock,
            AnalyticsBlock, PartnersBlock, ContactsBlock,
            Advantage, Partner
        )
        
        print("\n" + "="*60)
        print("СОЗДАНИЕ/ОБНОВЛЕНИЕ БЛОКОВ ГЛАВНОЙ СТРАНИЦЫ")
        print("="*60)
        
        # 1. Приветственный блок (обязательно с pk=1 для django-solo)
        hero_block, hero_created = HeroBlock.objects.get_or_create(
            pk=1,
            defaults={
                'title': "АО «Уголь-Транс»",
                'subtitle': "Ведущий оператор железнодорожных грузоперевозок угля в России. Основана в 1998 году. Ежегодно перевозим более 50 миллионов тонн грузов.",
                'cta_button_text': "Связаться с нами",
                'show_news_carousel': True,
                'news_display_type': 'all_active',
                'news_count': 5,
                'is_active': True
            }
        )
        if hero_created:
            print("✅ Приветственный блок создан")
        else:
            # Обновляем существующий блок
            hero_block.title = "АО «Уголь-Транс»"
            hero_block.subtitle = "Ведущий оператор железнодорожных грузоперевозок угля в России. Основана в 1998 году. Ежегодно перевозим более 50 миллионов тонн грузов."
            hero_block.cta_button_text = "Связаться с нами"
            hero_block.show_news_carousel = True
            hero_block.news_display_type = 'all_active'
            hero_block.news_count = 5
            hero_block.is_active = True
            hero_block.save()
            print("✅ Приветственный блок обновлен")
        
        # 2. Блок 'Бизнес-аналитика'
        analytics_block, analytics_created = AnalyticsBlock.objects.get_or_create(
            pk=1,
            defaults={
                'title': "Бизнес-аналитика и ключевые показатели",
                'subtitle': "Цифры, которые говорят сами за себя",
                'content': "Ежегодный объем перевозок: более 50 млн тонн. Парк компании: 15,000 вагонов, 80 локомотивов. География работы: от Кузбасса до портов Балтийского моря и Дальнего Востока.",
                'is_active': True
            }
        )
        if analytics_created:
            print("✅ Блок 'Бизнес-аналитика' создан")
        else:
            analytics_block.title = "Бизнес-аналитика и ключевые показатели"
            analytics_block.subtitle = "Цифры, которые говорят сами за себя"
            analytics_block.content = "Ежегодный объем перевозок: более 50 млн тонн. Парк компании: 15,000 вагонов, 80 локомотивов. География работы: от Кузбасса до портов Балтийского моря и Дальнего Востока."
            analytics_block.is_active = True
            analytics_block.save()
            print("✅ Блок 'Бизнес-аналитика' обновлен")
        
        # 3. Блок 'Контакты'
        contacts_block, contacts_created = ContactsBlock.objects.get_or_create(
            pk=1,
            defaults={
                'title': "Контакты",
                'subtitle': "Свяжитесь с нами для сотрудничества",
                'content': "Головной офис: г. Кемерово, ул. Ноградская, 5. Телефон: +7 (3842) 45-67-89. Email: office@ugol-trans.ru. Отдел логистики: +7 (3842) 45-67-90.",
                'cta_button_text': "Перейти к контактам",
                'is_active': True
            }
        )
        if contacts_created:
            print("✅ Блок 'Контакты' создан")
        else:
            contacts_block.title = "Контакты"
            contacts_block.subtitle = "Свяжитесь с нами для сотрудничества"
            contacts_block.content = "Головной офис: г. Кемерово, ул. Ноградская, 5. Телефон: +7 (3842) 45-67-89. Email: office@ugol-trans.ru. Отдел логистики: +7 (3842) 45-67-90."
            contacts_block.cta_button_text = "Перейти к контактам"
            contacts_block.is_active = True
            contacts_block.save()
            print("✅ Блок 'Контакты' обновлен")
        
        # 4. Блок 'О компании'
        about_block, about_created = AboutBlock.objects.get_or_create(
            pk=1,
            defaults={
                'title': "О компании АО «Уголь-Транс»",
                'subtitle': "25 лет на рынке железнодорожных перевозок",
                'content': "АО «Уголь-Транс» — системообразующее предприятие в сфере железнодорожных грузоперевозок России. Специализируемся на перевозках угля, кокса и сырьевых грузов. Входим в топ-5 операторов угольных перевозок страны.",
                'is_active': True
            }
        )
        if about_created:
            print("✅ Блок 'О компании' создан")
        else:
            about_block.title = "О компании АО «Уголь-Транс»"
            about_block.subtitle = "25 лет на рынке железнодорожных перевозок"
            about_block.content = "АО «Уголь-Транс» — системообразующее предприятие в сфере железнодорожных грузоперевозок России. Специализируемся на перевозках угля, кокса и сырьевых грузов. Входим в топ-5 операторов угольных перевозок страны."
            about_block.is_active = True
            about_block.save()
            print("✅ Блок 'О компании' обновлен")
        
        # 5. Блок 'Партнеры'
        partners_block, partners_created = PartnersBlock.objects.get_or_create(
            pk=1,
            defaults={
                'title': "Наши партнеры",
                'subtitle': "Сотрудничество с лидерами промышленности и энергетики",
                'content': "Мы работаем с крупнейшими угледобывающими компаниями Кузбасса, металлургическими комбинатами и энергогенерирующими компаниями России.",
                'is_active': True
            }
        )
        if partners_created:
            print("✅ Блок 'Партнеры' создан")
        else:
            partners_block.title = "Наши партнеры"
            partners_block.subtitle = "Сотрудничество с лидерами промышленности и энергетики"
            partners_block.content = "Мы работаем с крупнейшими угледобывающими компаниями Кузбасса, металлургическими комбинатами и энергогенерирующими компаниями России."
            partners_block.is_active = True
            partners_block.save()
            print("✅ Блок 'Партнеры' обновлен")
        
        # Создаем/обновляем партнеров (без логотипов)
        partners_data = [
            {'name': 'СУЭК', 'website': 'https://www.suek.ru', 'order': 1},
            {'name': 'Кузбассразрезуголь', 'website': 'https://www.kru.ru', 'order': 2},
            {'name': 'Мечел', 'website': 'https://www.mechel.ru', 'order': 3},
            {'name': 'ЕВРАЗ', 'website': 'https://www.evraz.com', 'order': 4},
            {'name': 'Русэнергосбыт', 'website': 'https://www.rusenergosbyt.ru', 'order': 5},
        ]
        
        for i, partner_data in enumerate(partners_data, 1):
            Partner.objects.update_or_create(
                partners_block=partners_block,
                order=i,
                defaults={
                    'name': partner_data['name'],
                    'website': partner_data['website'],
                    'is_active': True
                }
            )
        print("   ✅ Партнеры созданы/обновлены (5 записей)")
        
        # 6. Блок 'Преимущества'
        advantage_block, advantage_created = AdvantageBlock.objects.get_or_create(
            pk=1,
            defaults={
                'title': "Преимущества работы с нами",
                'subtitle': "Почему компании выбирают АО «Уголь-Транс»",
                'content': "Сочетание многолетнего опыта с современными технологиями и индивидуальным подходом к каждому клиенту.",
                'is_active': True
            }
        )
        if advantage_created:
            print("✅ Блок 'Преимущества' создан")
        else:
            advantage_block.title = "Преимущества работы с нами"
            advantage_block.subtitle = "Почему компании выбирают АО «Уголь-Транс»"
            advantage_block.content = "Сочетание многолетнего опыта с современными технологиями и индивидуальным подходом к каждому клиенту."
            advantage_block.is_active = True
            advantage_block.save()
            print("✅ Блок 'Преимущества' обновлен")
        
        # Создаем/обновляем преимущества (без иконок)
        advantages_data = [
            {
                'title': 'Собственный подвижной состав',
                'description': 'Более 15,000 вагонов и 80 локомотивов, проходящих регулярное техническое обслуживание',
                'order': 1
            },
            {
                'title': 'Опытная команда',
                'description': '25 лет на рынке, квалифицированные специалисты с отраслевым опытом более 10 лет',
                'order': 2
            },
            {
                'title': 'Широкая география',
                'description': 'Перевозки по всей России от Кузбасса до портов Балтийского моря и Дальнего Востока',
                'order': 3
            },
            {
                'title': 'Современные технологии',
                'description': 'GPS-мониторинг в реальном времени, электронный документооборот, цифровая логистика',
                'order': 4
            },
            {
                'title': 'Гибкая тарифная политика',
                'description': 'Индивидуальные условия для постоянных клиентов и объемных перевозок',
                'order': 5
            },
            {
                'title': 'Надежность и безопасность',
                'description': 'Полное страхование грузов, соблюдение всех нормативов, минимальные риски',
                'order': 6
            },
        ]
        
        for i, advantage_data in enumerate(advantages_data, 1):
            Advantage.objects.update_or_create(
                advantage_block=advantage_block,
                order=i,
                defaults={
                    'title': advantage_data['title'],
                    'description': advantage_data['description'],
                    'is_active': True
                }
            )
        print("   ✅ Преимущества созданы/обновлены (6 записей)")
        
        print("="*60)
        print("ВСЕ БЛОКИ УСПЕШНО СОЗДАНЫ/ОБНОВЛЕНЫ!")
        print("="*60 + "\n")