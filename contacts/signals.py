from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_test_contacts(sender, **kwargs):
    """Автоматически создает тестовые контакты при миграциях"""
    if sender.name == 'contacts':
        print("\n" + "="*60)
        print("НАЧАЛО СОЗДАНИЯ КОНТАКТОВ...")
        print("="*60)
        
        try:
            from .models import Phone, Email, Address, SocialMedia
            
            # 1. Телефоны
            phones_data = [
                {
                    'number': '+7 (3842) 45-67-89',
                    'description': 'Головной офис, общие вопросы',
                    'order': 1,
                    'is_active': True
                },
                {
                    'number': '+7 (3842) 45-67-90',
                    'description': 'Отдел логистики и планирования',
                    'order': 2,
                    'is_active': True
                },
                {
                    'number': '+7 (3842) 45-67-91',
                    'description': 'Отдел продаж и клиентского сервиса',
                    'order': 3,
                    'is_active': True
                },
                {
                    'number': '+7 (3842) 45-67-92',
                    'description': 'Бухгалтерия, финансовые вопросы',
                    'order': 4,
                    'is_active': True
                },
                {
                    'number': '+7 (800) 555-35-35',
                    'description': 'Бесплатная горячая линия',
                    'order': 5,
                    'is_active': True
                },
            ]
            
            for i, phone_data in enumerate(phones_data, 1):
                Phone.objects.update_or_create(
                    number=phone_data['number'],
                    defaults={
                        'description': phone_data['description'],
                        'order': phone_data['order'],
                        'is_active': phone_data['is_active']
                    }
                )
            print("✅ Телефоны созданы/обновлены (5 записей)")
            
            # 2. Email адреса
            emails_data = [
                {
                    'address': 'office@ugol-trans.ru',
                    'description': 'Головной офис, общие вопросы',
                    'order': 1,
                    'is_active': True
                },
                {
                    'address': 'logistics@ugol-trans.ru',
                    'description': 'Отдел логистики и планирования перевозок',
                    'order': 2,
                    'is_active': True
                },
                {
                    'address': 'sales@ugol-trans.ru',
                    'description': 'Отдел продаж и заключения договоров',
                    'order': 3,
                    'is_active': True
                },
                {
                    'address': 'accounting@ugol-trans.ru',
                    'description': 'Бухгалтерия, финансовые документы',
                    'order': 4,
                    'is_active': True
                },
                {
                    'address': 'safety@ugol-trans.ru',
                    'description': 'Отдел охраны труда и техники безопасности',
                    'order': 5,
                    'is_active': True
                },
            ]
            
            for i, email_data in enumerate(emails_data, 1):
                Email.objects.update_or_create(
                    address=email_data['address'],
                    defaults={
                        'description': email_data['description'],
                        'order': email_data['order'],
                        'is_active': email_data['is_active']
                    }
                )
            print("✅ Email адреса созданы/обновлены (5 записей)")
            
            # 3. Адреса
            addresses_data = [
                {
                    'text': '650000, г. Кемерово, ул. Ноградская, д. 5',
                    'description': 'Головной офис АО «Уголь-Транс»',
                    'map_link': 'https://yandex.ru/maps/65/kemerovo/?ll=86.087314%2C55.354968&mode=search&oid=1138908735&ol=biz&z=17',
                    'order': 1,
                    'is_active': True
                },
                {
                    'text': '650099, г. Кемерово, пр-т Советский, д. 58',
                    'description': 'Операционный центр и диспетчерская служба',
                    'map_link': 'https://yandex.ru/maps/65/kemerovo/?ll=86.089671%2C55.347592&mode=search&oid=1046919695&ol=biz&z=17',
                    'order': 2,
                    'is_active': True
                },
                {
                    'text': '652600, г. Ленинск-Кузнецкий, ул. Топкинская, д. 12',
                    'description': 'Локомотивное депо и ремонтная база',
                    'map_link': 'https://yandex.ru/maps/11309/leninsk-kuzneckij/?ll=86.178846%2C54.674163&mode=search&oid=1227736498&ol=biz&z=17',
                    'order': 3,
                    'is_active': True
                },
                {
                    'text': '652800, г. Белово, ул. Железнодорожная, д. 47',
                    'description': 'Сортировочная станция и склад временного хранения',
                    'map_link': 'https://yandex.ru/maps/11304/belovo/?ll=86.285488%2C54.416015&mode=search&oid=1769989101&ol=biz&z=17',
                    'order': 4,
                    'is_active': True
                },
                {
                    'text': '652840, г. Новокузнецк, ул. Запсибовская, д. 25',
                    'description': 'Южное региональное отделение',
                    'map_link': 'https://yandex.ru/maps/11319/novokuzneck/?ll=87.109097%2C53.757110&mode=search&oid=2113345408&ol=biz&z=17',
                    'order': 5,
                    'is_active': True
                },
            ]
            
            for i, address_data in enumerate(addresses_data, 1):
                Address.objects.update_or_create(
                    text=address_data['text'],
                    defaults={
                        'description': address_data['description'],
                        'map_link': address_data['map_link'],
                        'order': address_data['order'],
                        'is_active': address_data['is_active']
                    }
                )
            print("✅ Адреса созданы/обновлены (5 записей)")
            
            # 4. Социальные сети (без иконок)
            socials_data = [
                {
                    'name': 'ВКонтакте',
                    'url': 'https://vk.com/ugol_trans',
                    'order': 1,
                    'is_active': True
                },
                {
                    'name': 'Telegram',
                    'url': 'https://t.me/ugol_trans_company',
                    'order': 2,
                    'is_active': True
                },
                {
                    'name': 'Одноклассники',
                    'url': 'https://ok.ru/group/ugoltrans',
                    'order': 3,
                    'is_active': True
                },
                {
                    'name': 'Rutube',
                    'url': 'https://rutube.ru/channel/ugol-trans/',
                    'order': 4,
                    'is_active': True
                },
                {
                    'name': 'YouTube',
                    'url': 'https://www.youtube.com/@ugol_trans',
                    'order': 5,
                    'is_active': True
                },
            ]
            
            for i, social_data in enumerate(socials_data, 1):
                SocialMedia.objects.update_or_create(
                    name=social_data['name'],
                    defaults={
                        'url': social_data['url'],
                        'order': social_data['order'],
                        'is_active': social_data['is_active'],
                        'icon': None
                    }
                )
            print("✅ Социальные сети созданы/обновлены (5 записей)")
            
            print("="*60)
            print("КОНТАКТЫ АО «Уголь-Транс» УСПЕШНО СОЗДАНЫ!")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"❌ ОШИБКА при создании контактов: {e}")
            import traceback
            traceback.print_exc()