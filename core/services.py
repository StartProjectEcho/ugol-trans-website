# core/services.py
"""
Сервисные классы для бизнес-логики.
"""
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.template.loader import render_to_string
import logging
from time import sleep

logger = logging.getLogger(__name__)


class EmailService:
    """
    Сервис для отправки email уведомлений.
    """
    
    @staticmethod
    def validate_email(email):
        """
        Валидация email адреса.
        """
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False
    
    @staticmethod
    def send_application_notification(application):
        """
        Отправка уведомления о новой заявке.
        
        Returns:
            bool: True если отправка успешна
        """
        from core.models import SiteSettings
        
        try:
            site_settings = SiteSettings.objects.get()
        except SiteSettings.DoesNotExist:
            logger.warning("SiteSettings не найдены")
            return False
        
        recipient_list = site_settings.get_notification_emails_list()
        if not recipient_list:
            logger.warning("Нет email для уведомлений")
            return False
        
        # Валидация email получателей
        valid_recipients = []
        for email in recipient_list:
            if EmailService.validate_email(email):
                valid_recipients.append(email)
            else:
                logger.warning(f"Некорректный email в списке уведомлений: {email}")
        
        if not valid_recipients:
            logger.warning("Нет валидных email для уведомлений")
            return False
        
        subject = f'Новая заявка от {application.name} - {site_settings.site_name}'
        
        # Генерируем HTML и текстовую версии письма
        context = {
            'application': application,
            'site_name': site_settings.site_name,
            'company_name': site_settings.company_full_name,
        }
        
        try:
            html_message = render_to_string('emails/application_notification.html', context)
            plain_message = render_to_string('emails/application_notification.txt', context)
        except Exception as e:
            logger.error(f"Ошибка загрузки шаблонов email: {e}")
            # Фолбэк если шаблонов нет
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
                    .content {{ background: #f9f9f9; padding: 20px; }}
                    .field {{ margin-bottom: 15px; }}
                    .label {{ font-weight: bold; color: #2c3e50; }}
                    .footer {{ background: #ecf0f1; padding: 15px; text-align: center; font-size: 12px; color: #7f8c8d; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Новая заявка с сайта</h1>
                        <p>{site_settings.site_name}</p>
                    </div>
                    
                    <div class="content">
                        <div class="field">
                            <span class="label">👤 Имя клиента:</span> {application.name}
                        </div>
                        <div class="field">
                            <span class="label">📞 Телефон:</span> {application.phone or 'Не указан'}
                        </div>
                        <div class="field">
                            <span class="label">✉️ Email:</span> {application.email or 'Не указан'}
                        </div>
                        <div class="field">
                            <span class="label">💬 Сообщение:</span><br>
                            {application.message}
                        </div>
                        <div class="field">
                            <span class="label">📅 Дата отправки:</span> {application.created_at.strftime('%d.%m.%Y %H:%M')}
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>Это автоматическое уведомление от системы сайта {site_settings.site_name}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            plain_message = f"НОВАЯ ЗАЯВКА С САЙТА {site_settings.site_name}\n\n"
            plain_message += f"Имя клиента: {application.name}\n"
            plain_message += f"Телефон: {application.phone or 'Не указан'}\n"
            plain_message += f"Email: {application.email or 'Не указан'}\n"
            plain_message += f"Сообщение: \n{application.message}\n\n"
            plain_message += f"Дата отправки: {application.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            plain_message += f"---\nЭто автоматическое уведомление от системы сайта {site_settings.site_name}"
        
        try:
            from_email = site_settings.default_email_from or getattr(
                settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER
            )
            
            # Проверяем валидность email отправителя
            if not EmailService.validate_email(from_email):
                logger.warning(f"Некорректный email отправителя: {from_email}")
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER)
            
            # Лимит отправки писем (предотвращение спама)
            sleep(1)
            
            # Создаем соединение и отправляем
            connection = get_connection(
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                fail_silently=False,
            )
            
            email = EmailMultiAlternatives(
                subject=subject.strip(),
                body=plain_message.strip(),
                from_email=from_email,
                to=valid_recipients,
                connection=connection,
            )
            email.attach_alternative(html_message, "text/html")
            
            # Дополнительные заголовки для лучшей доставляемости
            email.extra_headers = {
                'X-Priority': '3',
                'X-Mailer': 'Django Mail Service',
                'Precedence': 'bulk',
            }
            
            email.send()
            
            logger.info(f"Email успешно отправлен для заявки #{application.id} на {len(valid_recipients)} адрес(ов)")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки email для заявки #{application.id}: {str(e)}", exc_info=True)
            return False
    
    @staticmethod
    def test_connection():
        """
        Тестирование подключения к SMTP серверу.
        
        Returns:
            tuple: (success, message)
        """
        try:
            connection = get_connection(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS,
                use_ssl=settings.EMAIL_USE_SSL,
                timeout=getattr(settings, 'EMAIL_TIMEOUT', 30),
            )
            connection.open()
            connection.close()
            return True, "SMTP соединение успешно установлено"
        except Exception as e:
            return False, f"Ошибка SMTP соединения: {str(e)}"