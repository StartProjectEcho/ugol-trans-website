"""
Модели приложения core.
"""
from django.db import models
from django.core.validators import FileExtensionValidator
from solo.models import SingletonModel
import os


class TimeStampedModel(models.Model):
    """
    Абстрактная модель с временными метками.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']


class StatusModel(TimeStampedModel):
    """
    Абстрактная модель для объектов, которые могут быть активны/неактивны.
    """
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно",
        help_text="Отображать на сайте"
    )
    
    class Meta:
        abstract = True


class SortableModel(models.Model):
    """
    Абстрактная модель для сортируемых объектов.
    """
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок",
        db_index=True
    )
    
    class Meta:
        abstract = True
        ordering = ['order']


class SiteSettings(SingletonModel):
    """
    Настройки сайта (синглтон).
    """
    site_name = models.CharField(
        max_length=200,
        default="АО «Уголь-Транс»",
        verbose_name="Название сайта"
    )
    company_full_name = models.CharField(
        max_length=300,
        default="Акционерное общество «Уголь-Транс»",
        verbose_name="Полное название компании"
    )
    logo = models.ForeignKey(
        'Image',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Логотип компании",
        related_name='site_logos'
    )
    favicon = models.ForeignKey(
        'Image',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Фавикон",
        related_name='site_favicons'  
    )
    notification_emails = models.TextField(
        blank=True,
        verbose_name="Email для уведомлений",
        help_text="Адреса для уведомлений о новых заявках (через запятую)"
    )
    recaptcha_site_key = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="reCAPTCHA Site Key"
    )
    recaptcha_secret_key = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="reCAPTCHA Secret Key"
    )
    yandex_metrica_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Яндекс.Метрика ID"
    )
    default_email_from = models.EmailField(
        blank=True,
        verbose_name="Email отправителя по умолчанию"
    )

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Настройки сайта"
    
    def get_notification_emails_list(self):
        """
        Возвращает список email для уведомлений.
        """
        if not self.notification_emails:
            return []
        return [email.strip() for email in self.notification_emails.split(',') if email.strip()]


class Image(StatusModel):
    """
    Модель для хранения изображений с кэшированием размеров.
    """
    image = models.ImageField(
        upload_to='images/%Y/%m/%d/',
        verbose_name="Изображение",
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'gif']
            )
        ]
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,  # Делаем поле необязательным
        verbose_name="Alt текст",
        help_text="Описание изображения для SEO"
    )
    # Кэшированные размеры для быстрого доступа
    image_width = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Ширина (px)"
    )
    image_height = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Высота (px)"
    )
    file_size = models.PositiveBigIntegerField(
        blank=True,
        null=True,
        verbose_name="Размер файла (байты)"
    )

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['alt_text']),
        ]

    def __str__(self):
        """Безопасный __str__ метод."""
        if self.alt_text:
            return self.alt_text
        elif self.id:
            return f"Изображение #{self.id}"
        elif self.image:
            # Если еще нет id (при создании), используем имя файла
            try:
                return self.image.name.split('/')[-1]
            except (AttributeError, ValueError):
                return "Новое изображение"
        return "Изображение"
    
    def save(self, *args, **kwargs):
        """Сохранение с вычислением размеров изображения."""
        # Сохраняем модель
        super().save(*args, **kwargs)
        
        # После сохранения вычисляем размеры, если они не вычислены
        if self.image and (not self.image_width or not self.image_height or not self.file_size):
            self._calculate_and_update_dimensions()
    
    def _calculate_and_update_dimensions(self):
        """Вычисление размеров изображения после сохранения."""
        try:
            # Проверяем существование файла
            if hasattr(self.image, 'path'):
                file_path = self.image.path
                
                if os.path.exists(file_path):
                    # Вычисляем размер файла
                    self.file_size = os.path.getsize(file_path)
                    
                    # Вычисляем размеры изображения
                    from PIL import Image as PILImage
                    try:
                        img = PILImage.open(file_path)
                        self.image_width, self.image_height = img.size
                        
                        # Сохраняем обновленные поля без вызова полного save()
                        Image.objects.filter(pk=self.pk).update(
                            image_width=self.image_width,
                            image_height=self.image_height,
                            file_size=self.file_size
                        )
                    except Exception as e:
                        # Если не удалось открыть как изображение (может быть повреждено)
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Не удалось открыть изображение {file_path}: {e}")
                        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Ошибка вычисления размеров изображения #{self.pk}: {e}")
    
    @property
    def url(self):
        """URL изображения с проверкой существования."""
        try:
            if self.image:
                return self.image.url
        except (ValueError, AttributeError):
            pass
        return None
    
    @property
    def filename(self):
        """Имя файла изображения."""
        try:
            if self.image:
                return self.image.name.split('/')[-1]
        except (AttributeError, ValueError):
            pass
        return ""
    
    @property
    def size_display(self):
        """Человекочитаемый размер файла из кэша."""
        if self.file_size:
            size = self.file_size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
        return "—"
    
    @property
    def width_height(self):
        """Ширина и высота изображения из кэша."""
        if self.image_width and self.image_height:
            return f"{self.image_width}x{self.image_height}"
        return "—"
    
    @property
    def recommended_usage(self):
        """
        Рекомендуемое использование в зависимости от размера.
        """
        if self.image_width and self.image_height:
            if self.image_width >= 1920 and self.image_height >= 1080:
                return "Фоновое изображение, баннер"
            elif self.image_width >= 800 and self.image_height >= 600:
                return "Основное изображение, логотип"
            elif self.image_width >= 200 and self.image_height >= 200:
                return "Иконка, аватар"
            elif self.image_width >= 64 and self.image_height >= 64:
                return "Маленькая иконка, фавикон"
            else:
                return "Мелкая графика"
        return "—"
    
    def file_exists(self):
        """Проверяет существует ли файл на диске."""
        try:
            if self.image and hasattr(self.image, 'path'):
                return os.path.exists(self.image.path)
        except (AttributeError, ValueError):
            pass
        return False


class File(StatusModel):
    """
    Модель для хранения файлов.
    """
    file = models.FileField(
        upload_to='files/%Y/%m/%d/',
        verbose_name="Файл",
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 
                                   'ppt', 'pptx', 'zip', 'rar', 'txt']
            )
        ]
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Название файла"
    )
    # Кэшированный размер файла
    file_size = models.PositiveBigIntegerField(
        blank=True,
        null=True,
        verbose_name="Размер файла (байты)"
    )

    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        """Безопасный __str__ метод."""
        if self.name:
            return self.name
        elif self.id:
            return f"Файл #{self.id}"
        elif self.file:
            try:
                return self.file.name.split('/')[-1]
            except (AttributeError, ValueError):
                return "Новый файл"
        return "Файл"
    
    def save(self, *args, **kwargs):
        """Сохранение с вычислением размера файла."""
        super().save(*args, **kwargs)
        
        # После сохранения вычисляем размер файла
        if self.file and not self.file_size:
            self._calculate_and_update_size()
    
    def _calculate_and_update_size(self):
        """Вычисление размера файла после сохранения."""
        try:
            if hasattr(self.file, 'path') and os.path.exists(self.file.path):
                self.file_size = os.path.getsize(self.file.path)
                File.objects.filter(pk=self.pk).update(file_size=self.file_size)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Ошибка вычисления размера файла #{self.pk}: {e}")
    
    @property
    def url(self):
        """URL файла."""
        try:
            if self.file:
                return self.file.url
        except ValueError:
            pass
        return None
    
    @property
    def extension(self):
        """Расширение файла."""
        try:
            if self.file and '.' in self.file.name:
                return self.file.name.split('.')[-1].upper()
        except (AttributeError, ValueError):
            pass
        return None
    
    @property
    def size_display(self):
        """Человекочитаемый размер файла из кэша."""
        if self.file_size:
            size = self.file_size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
        return "—"
    
    @property
    def filename(self):
        """Имя файла."""
        try:
            if self.file:
                return self.file.name.split('/')[-1]
        except (AttributeError, ValueError):
            pass
        return ""
    
    @property
    def file_type(self):
        """Тип файла для отображения."""
        ext = self.extension.lower() if self.extension else ""
        
        file_types = {
            'pdf': 'PDF документ',
            'doc': 'Документ Word',
            'docx': 'Документ Word',
            'xls': 'Таблица Excel',
            'xlsx': 'Таблица Excel',
            'ppt': 'Презентация',
            'pptx': 'Презентация',
            'zip': 'Архив ZIP',
            'rar': 'Архив RAR',
            'txt': 'Текстовый файл',
        }
        
        return file_types.get(ext, f"Файл {ext.upper()}" if ext else "Файл")
    
    def file_exists(self):
        """Проверяет существует ли файл на диске."""
        try:
            if self.file and hasattr(self.file, 'path'):
                return os.path.exists(self.file.path)
        except (AttributeError, ValueError):
            pass
        return False