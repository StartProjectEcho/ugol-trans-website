# core/management/commands/test_email.py
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import socket


class Command(BaseCommand):
    help = 'Тестирование SMTP подключения и отправки email'
    
    def handle(self, *args, **options):
        self.stdout.write("Тестирование email настроек...")
        
        # Показываем текущие настройки
        self.stdout.write(f"\nТекущие настройки:")
        self.stdout.write(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"  EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
        self.stdout.write(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        # Проверка соединения
        try:
            self.stdout.write("\nПроверка соединения с SMTP сервером...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((settings.EMAIL_HOST, settings.EMAIL_PORT))
            sock.close()
            
            if result == 0:
                self.stdout.write(self.style.SUCCESS(f"✓ SMTP порт {settings.EMAIL_PORT} доступен"))
            else:
                self.stdout.write(self.style.ERROR(f"✗ SMTP порт {settings.EMAIL_PORT} недоступен"))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Ошибка проверки порта: {e}"))
            return
        
        # Отправка тестового email
        self.stdout.write("\nОтправка тестового email...")
        try:
            send_mail(
                subject='Тестовое письмо от сайта АО Уголь-Транс',
                message='Это тестовое письмо для проверки настроек SMTP.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS("✓ Тестовый email успешно отправлен!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Ошибка отправки email: {e}"))