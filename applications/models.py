from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import TimeStampedModel
import re


class Application(TimeStampedModel):
    """
    Модель для заявок с клиентами.
    """
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('processed', 'Обработана'),
        ('rejected', 'Отклонена'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name="Имя клиента"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Телефон",
        help_text="Формат: +7 999 123-45-67"
    )
    email = models.EmailField(
        blank=True,
        verbose_name="Email адрес"
    )
    message = models.TextField(
        max_length=1000,
        verbose_name="Сообщение"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Статус обработки"
    )
    manager_comment = models.TextField(
        max_length=500,
        blank=True,
        verbose_name="Комментарий менеджера"
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата обработки"
    )

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Заявка от {self.name} ({self.created_at.strftime('%d.%m.%Y')})"

    def clean(self):
        """
        Валидация данных заявки.
        """
        super().clean()
        
        # Проверка контактов
        if not self.phone and not self.email:
            raise ValidationError("Необходимо указать либо телефон, либо email адрес.")
        
        # Валидация телефона
        if self.phone:
            self._validate_phone()
        
        # Валидация email
        if self.email:
            self._validate_email()
    
    def _validate_phone(self):
        """
        Валидация номера телефона.
        """
        # Очищаем телефон от лишних символов
        clean_phone = re.sub(r'[^\d\+]', '', self.phone)
        
        # Проверяем формат
        phone_regex = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
        
        if not re.match(phone_regex, clean_phone):
            raise ValidationError({
                'phone': 'Введите корректный номер телефона в формате: +7 999 123-45-67'
            })
        
        # Сохраняем очищенный номер
        self.phone = clean_phone
    
    def _validate_email(self):
        """
        Валидация email адреса.
        """
        # Проверяем формат email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, self.email):
            raise ValidationError({
                'email': 'Введите корректный email адрес'
            })
    
    def save(self, *args, **kwargs):
        """
        Переопределяем save для автоматической установки даты обработки.
        """
        is_new = not self.pk
        
        # Автоматически устанавливаем дату обработки при смене статуса
        if self.status == 'processed' and not self.processed_at:
            self.processed_at = timezone.now()
        elif self.status != 'processed':
            self.processed_at = None
            
        # Валидируем перед сохранением
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Отправляем уведомление только для НОВЫХ заявок
        if is_new:
            try:
                from core.services import EmailService
                EmailService.send_application_notification(self)
            except Exception as e:
                # Логируем ошибку, но не прерываем сохранение
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Ошибка отправки уведомления для заявки #{self.id}: {e}")
    
    @property
    def contact_info(self):
        """
        Возвращает контактную информацию в читаемом формате.
        """
        contact = []
        if self.phone:
            contact.append(f"📞 {self.phone}")
        if self.email:
            contact.append(f"✉️ {self.email}")
        return " | ".join(contact) if contact else "—"
    
    @property
    def message_preview(self):
        """
        Краткий предпросмотр сообщения.
        """
        if self.message:
            return self.message[:50] + "..." if len(self.message) > 50 else self.message
        return ""
    
    @property
    def status_color(self):
        """
        Цвет статуса для визуального отображения.
        """
        colors = {
            'new': '#FFA500',      # orange
            'in_progress': '#1E90FF',  # blue
            'processed': '#32CD32',    # green
            'rejected': '#DC143C',     # red
        }
        return colors.get(self.status, '#808080')
    
    @property
    def days_since_creation(self):
        """
        Количество дней с момента создания заявки.
        """
        if self.created_at:
            delta = timezone.now() - self.created_at
            return delta.days
        return 0
    
    def get_status_display_formatted(self):
        """
        Форматированное отображение статуса с цветом.
        """
        status_display = self.get_status_display()
        colors = {
            'new': '🟠',
            'in_progress': '🔵',
            'processed': '🟢',
            'rejected': '🔴',
        }
        icon = colors.get(self.status, '⚫')
        return f"{icon} {status_display}"
    
    def get_age_display(self):
        """
        Человекочитаемое отображение возраста заявки с учетом статуса.
        """
        from django.utils.html import format_html
        days = self.days_since_creation
        
        # Определяем отображение в зависимости от статуса
        if self.status == 'processed':
            # Обработанные - серый нейтральный
            return format_html('<span style="color: #808080;">{}</span>', f"{days} д.")
        
        elif self.status == 'rejected':
            # Отклоненные - серый нейтральный
            return format_html('<span style="color: #808080;">{}</span>', f"{days} д.")
        
        elif self.status == 'in_progress':
            # В работе - синий
            if days == 0:
                return "Сегодня"
            elif days == 1:
                return "Вчера"
            else:
                return format_html('<span style="color: #1E90FF;">{}</span>', f"{days} д.")
        
        else:  # new - новые
            if days == 0:
                return "Сегодня"
            elif days == 1:
                return "Вчера"
            else:
                # Новые становятся красными если долго ждут
                if days > 3:
                    return format_html('<span style="color: #DC143C; font-weight: bold;">{}</span>', f"{days} д.")
                elif days > 1:
                    return format_html('<span style="color: #FFA500;">{}</span>', f"{days} д.")
                else:
                    return format_html('<span style="color: #32CD32;">{}</span>', f"{days} д.")