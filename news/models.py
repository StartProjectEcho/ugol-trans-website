from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from core.models import StatusModel, SortableModel, Image, File


class News(StatusModel):
    """
    Модель новости.
    """
    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок новости"
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name="URL-адрес",
        help_text="Латинские буквы, цифры, дефисы, подчеркивания"
    )
    short_description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="Краткое описание",
        help_text="Краткое описание для превью (макс. 300 символов)"
    )
    main_image = models.ForeignKey(
        Image,
        on_delete=models.PROTECT,
        verbose_name="Главное изображение",
        help_text="Основное изображение для превью новости",
        null=True,
        blank=True
    )
    content = models.TextField(
        verbose_name="Текст новости",
        help_text="Полный текст новости"
    )
    publish_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата публикации",
        help_text="Дата и время отображения новости на сайте"
    )

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-publish_date']
        indexes = [
            models.Index(fields=['publish_date', 'is_active']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title
    
    def clean(self):
        """
        Валидация данных новости.
        """
        super().clean()
        
        # Проверяем уникальность slug
        if News.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            raise ValidationError({
                'slug': 'Такой URL-адрес уже существует. Выберите другой.'
            })
    
    def save(self, *args, **kwargs):
        """
        Автогенерация slug из title если не указан.
        """
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=False)
        
        # Убеждаемся, что slug уникален
        original_slug = self.slug
        counter = 1
        while News.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
        
        super().save(*args, **kwargs)
    
    @property
    def is_published(self):
        """
        Проверяет, опубликована ли новость.
        """
        return self.is_active and self.publish_date <= timezone.now()
    
    @property
    def days_since_publication(self):
        """
        Количество дней с момента публикации.
        """
        if self.publish_date:
            delta = timezone.now() - self.publish_date
            return delta.days
        return 0
    
    @property
    def publication_status(self):
        """
        Статус публикации.
        """
        if not self.is_active:
            return "черновик"
        elif self.publish_date > timezone.now():
            return "запланирована"
        else:
            return "опубликована"
    
    @property
    def publication_status_color(self):
        """
        Цвет статуса публикации.
        """
        if not self.is_active:
            return "#808080"  # серый
        elif self.publish_date > timezone.now():
            return "#FFA500"  # оранжевый
        else:
            return "#32CD32"  # зеленый


class NewsImage(SortableModel):
    """
    Дополнительные изображения для новости.
    """
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name='news_images',
        verbose_name="Новость"
    )
    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        verbose_name="Изображение"
    )

    class Meta:
        verbose_name = "Дополнительное изображение"
        verbose_name_plural = "Дополнительные изображения"
        ordering = ['order']
        unique_together = ['news', 'image']

    def __str__(self):
        return f"Изображение для новости: {self.news.title}"


class NewsFile(SortableModel):
    """
    Прикрепленные файлы для новости.
    """
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name='news_files',
        verbose_name="Новость"
    )
    file = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        verbose_name="Файл"
    )

    class Meta:
        verbose_name = "Прикрепленный файл"
        verbose_name_plural = "Прикрепленные файлы"
        ordering = ['order']
        unique_together = ['news', 'file']

    def __str__(self):
        return f"Файл для новости: {self.news.title}"