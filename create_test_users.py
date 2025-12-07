import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ugol_trans_site.settings')
django.setup()

from accounts.models import User

def create_test_users():
    # Контент-менеджер
    content_manager, created = User.objects.get_or_create(
        username='content',
        defaults={
            'email': 'content@ugol-trans.ru',
            'first_name': 'Мария',
            'last_name': 'Петрова',
            'role': 'content_manager',
            'is_staff': True
        }
    )
    if created:
        content_manager.set_password('content123')
        content_manager.save()
        print('✅ Создан контент-менеджер: content / content123')

    # CRM-менеджер
    crm_manager, created = User.objects.get_or_create(
        username='crm',
        defaults={
            'email': 'crm@ugol-trans.ru',
            'first_name': 'Дмитрий',
            'last_name': 'Сидоров',
            'role': 'crm_manager',
            'is_staff': True
        }
    )
    if created:
        crm_manager.set_password('crm123')
        crm_manager.save()
        print('✅ Создан CRM-менеджер: crm / crm123')

    print('✅ Все тестовые пользователи созданы!')

if __name__ == '__main__':
    create_test_users()