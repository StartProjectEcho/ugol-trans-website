from django.db import models
from django.core.validators import URLValidator, validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from core.models import StatusModel, SortableModel, Image
import re


class Phone(StatusModel, SortableModel):
    """
    Телефоны компании с валидацией.
    """
    number = models.CharField(
        max_length=20,
        verbose_name="Номер телефона",
        help_text="Формат: +7 999 123-45-67"
    )
    description = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Описание",
        help_text="Например: Главный офис, Отдел продаж"
    )

    class Meta:
        verbose_name = "Телефон"
        verbose_name_plural = "Телефоны"
        ordering = ['order', 'id']

    def __str__(self):
        if self.description:
            return f"{self.number} ({self.description})"
        return self.number
    
    def clean(self):
        """
        Валидация номера телефона (как в accounts и applications).
        """
        super().clean()
        
        if self.number:
            self._validate_phone()
    
    def _validate_phone(self):
        """
        Валидация номера телефона.
        """
        # Очищаем телефон от лишних символов
        clean_phone = re.sub(r'[^\d\+]', '', self.number)
        
        # Проверяем формат
        phone_regex = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
        
        if not re.match(phone_regex, clean_phone):
            raise ValidationError({
                'number': 'Введите корректный номер телефона в формате: +7 999 123-45-67'
            })
        
        # Сохраняем очищенный номер
        self.number = clean_phone
    
    def save(self, *args, **kwargs):
        """
        Переопределяем save для автоматической валидации.
        """
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def formatted_number(self):
        """
        Отформатированный номер телефона.
        """
        import re
        # Убираем все нецифровые символы
        digits = re.sub(r'\D', '', self.number)
        
        if len(digits) == 11 and digits.startswith('7'):
            # Формат: +7 (999) 123-45-67
            return f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:]}"
        elif len(digits) == 10:
            # Формат: +7 (999) 123-45-67
            return f"+7 ({digits[0:3]}) {digits[3:6]}-{digits[6:8]}-{digits[8:]}"
        
        return self.number
    
    @property
    def is_active_display(self):
        """
        Отображение активности.
        """
        if self.is_active:
            return "✅"
        else:
            return "❌"


class Email(StatusModel, SortableModel):
    """
    Email-адреса компании.
    """
    address = models.EmailField(
        verbose_name="Email адрес"
    )
    description = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Описание",
        help_text="Например: Общие вопросы, Техническая поддержка"
    )

    class Meta:
        verbose_name = "Email"
        verbose_name_plural = "Email адреса"
        ordering = ['order', 'id']

    def __str__(self):
        if self.description:
            return f"{self.address} ({self.description})"
        return self.address
    
    def clean(self):
        """
        Дополнительная валидация email.
        """
        super().clean()
        
        if self.address:
            self._validate_email()
    
    def _validate_email(self):
        """
        Валидация email адреса.
        """
        try:
            validate_email(self.address)
        except ValidationError:
            raise ValidationError({
                'address': 'Введите корректный email адрес'
            })
    
    def save(self, *args, **kwargs):
        """
        Переопределяем save для автоматической валидации.
        """
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def domain(self):
        """
        Домен email адреса.
        """
        if '@' in self.address:
            return self.address.split('@')[1]
        return ""
    
    @property
    def is_active_display(self):
        """
        Отображение активности.
        """
        if self.is_active:
            return "✅"
        else:
            return "❌"


class Address(StatusModel, SortableModel):
    """
    Адреса компании.
    """
    text = models.CharField(
        max_length=300,
        verbose_name="Полный адрес"
    )
    description = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Описание",
        help_text="Например: Главный офис, Склад, Производство"
    )
    map_link = models.URLField(
        blank=True,
        verbose_name="Ссылка на карты",
        help_text="Ссылка на Яндекс.Карты или Google Maps",
        validators=[URLValidator()]
    )

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"
        ordering = ['order', 'id']

    def __str__(self):
        if self.description:
            return f"{self.text} ({self.description})"
        return self.text
    
    def clean(self):
        """
        Валидация адреса.
        """
        super().clean()
        
        if not self.text.strip():
            raise ValidationError({
                'text': 'Адрес не может быть пустым'
            })
    
    def save(self, *args, **kwargs):
        """
        Переопределяем save для автоматической валидации.
        """
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def short_address(self):
        """
        Краткий адрес (первые 50 символов).
        """
        if len(self.text) > 50:
            return self.text[:47] + '...'
        return self.text
    
    @property
    def is_yandex_map(self):
        """
        Проверяет, является ли ссылка Яндекс.Картами.
        """
        if not self.map_link:
            return False
        return 'yandex' in self.map_link.lower()
    
    @property
    def is_google_map(self):
        """
        Проверяет, является ли ссылка Google Maps.
        """
        if not self.map_link:
            return False
        return 'google' in self.map_link.lower()
    
    @property
    def is_active_display(self):
        """
        Отображение активности.
        """
        if self.is_active:
            return "✅"
        else:
            return "❌"


class SocialMedia(StatusModel, SortableModel):
    """
    Социальные сети компании.
    """
    icon = models.ForeignKey(
        Image,
        on_delete=models.PROTECT,
        verbose_name="Иконка",
        null=True,
        blank=True,
    )
    name = models.CharField(
        max_length=50,
        verbose_name="Название платформы"
    )
    url = models.URLField(
        verbose_name="Ссылка на профиль",
        validators=[URLValidator()]
    )

    class Meta:
        verbose_name = "Социальная сеть"
        verbose_name_plural = "Социальные сети"
        ordering = ['order', 'id']

    def __str__(self):
        return self.name
    
    def clean(self):
        """
        Валидация социальной сети.
        """
        super().clean()
        
        # Проверка обязательных полей
        if not self.name.strip():
            raise ValidationError({
                'name': 'Название не может быть пустым'
            })
        
        if not self.url.strip():
            raise ValidationError({
                'url': 'Ссылка не может быть пустой'
            })
        
        # Валидация URL
        try:
            URLValidator()(self.url)
        except ValidationError:
            raise ValidationError({
                'url': 'Введите корректную ссылку (начинается с http:// или https://)'
            })
        
        # Проверка размера иконки если есть
        if self.icon and self.icon.pk:
            self._validate_icon_size()
    
    def _validate_icon_size(self):
        """
        Проверка размера иконки.
        """
        max_size = getattr(settings, 'SOCIAL_MEDIA_MAX_ICON_SIZE', 2 * 1024 * 1024)  # 2MB
        
        if self.icon.image and self.icon.image.size > max_size:
            raise ValidationError({
                'icon': f'Размер иконки не должен превышать {max_size // (1024*1024)}MB'
            })
    
    def save(self, *args, **kwargs):
        """
        Переопределяем save для автоматической валидации.
        """
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def icon_url(self):
        """
        URL иконки.
        """
        if self.icon and self.icon.image:
            return self.icon.image.url
        return None
    
    @property
    def is_active_display(self):
        """
        Отображение активности.
        """
        if self.is_active:
            return "✅"
        else:
            return "❌"
    
    @property
    def recommended_icon_size(self):
        """
        Рекомендуемый размер иконки.
        """
        return getattr(settings, 'SOCIAL_MEDIA_ICON_SIZE', '48x48')