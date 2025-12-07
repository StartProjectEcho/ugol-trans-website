from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
import re


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('content_manager', 'Контент-менеджер'),
        ('crm_manager', 'Менеджер по заявкам'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='content_manager',
        verbose_name="Роль"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Телефон"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-date_joined']  # Новые пользователи сверху

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    def clean(self):
        """
        Валидация данных пользователя перед сохранением.
        """
        super().clean()
        
        # Валидация email
        if self.email:
            self._validate_email()
        
        # Валидация телефона
        if self.phone:
            self._validate_phone()
            self._check_phone_duplicate()
    
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
        
        # Проверяем дубликаты email (исключая текущего пользователя)
        duplicate = User.objects.filter(
            email=self.email
        ).exclude(pk=self.pk).first()
        
        if duplicate:
            raise ValidationError({
                'email': f'Этот email уже используется пользователем: {duplicate.get_full_name()}'
            })
    
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
    
    def _check_phone_duplicate(self):
        """
        Проверка на дубликаты телефона.
        """
        # Игнорируем пустые телефоны
        if not self.phone:
            return
        
        # Ищем дубликаты (исключая текущего пользователя)
        duplicate = User.objects.filter(
            phone=self.phone
        ).exclude(pk=self.pk).first()
        
        if duplicate:
            raise ValidationError({
                'phone': f'Этот телефон уже используется пользователем: {duplicate.get_full_name()}'
            })
    
    def save(self, *args, **kwargs):
        """
        Переопределяем save для автоматической валидации.
        """
        self.full_clean()  # Вызываем clean()
        super().save(*args, **kwargs)
    
    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_content_manager(self):
        return self.role == 'content_manager'

    @property
    def is_crm_manager(self):
        return self.role == 'crm_manager'
    
    @property
    def is_staff(self):
        """Доступ в админку только для определенных ролей"""
        return self.role in ['admin', 'crm_manager', 'content_manager']
    
    @property
    def is_superuser(self):
        """Суперпользователь = админ"""
        return self.role == 'admin'
    
    def has_perm(self, perm, obj=None):
        """
        Проверяет разрешение для пользователя.
        Админы имеют все разрешения, другие роли - только определенные.
        """
        if self.is_admin:
            return True
        
        # Для не-админов проверяем специфичные разрешения
        if perm:
            # Разрешения связанные с заявками для CRM-менеджеров
            if 'application' in perm.lower() and self.is_crm_manager:
                return True
            
            # Разрешения связанные с контентом для контент-менеджеров
            if any(keyword in perm.lower() for keyword in [
                'image', 'file', 'news', 'page', 'diagram', 'analytics',
                'section', 'contact', 'phone', 'email', 'address', 'social'
            ]) and self.is_content_manager:
                return True
        
        return False
    
    def has_module_perms(self, app_label):
        """
        Проверяет доступ к модулю (приложению).
        """
        if self.is_admin:
            return True
        
        # CRM-менеджеры видят только applications
        if self.is_crm_manager:
            return app_label == 'applications'
        
        # Контент-менеджеры видят: core, main_page, dynamic_pages, business_analytics, news
        if self.is_content_manager:
            return app_label in [
                'core', 'main_page', 'dynamic_pages', 
                'business_analytics', 'news', 'contacts'
            ]
        
        return False
    
    def get_role_display_formatted(self):
        """
        Форматированное отображение роли для админки.
        """
        role_icons = {
            'admin': '👑',
            'content_manager': '📝', 
            'crm_manager': '📞'
        }
        icon = role_icons.get(self.role, '👤')
        return f"{icon} {self.get_role_display()}"
    
    def get_last_login_display(self):
        """
        Человекочитаемое отображение последнего входа.
        """
        if not self.last_login:
            return "Никогда"
        
        from django.utils import timezone
        now = timezone.now()
        diff = now - self.last_login
        
        if diff.days == 0:
            if diff.seconds < 3600:
                minutes = diff.seconds // 60
                return f"Сегодня, {minutes} мин назад"
            return "Сегодня"
        elif diff.days == 1:
            return "Вчера"
        elif diff.days < 7:
            return f"{diff.days} дней назад"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} недель назад"
        else:
            months = diff.days // 30
            return f"{months} месяцев назад"