from django.db import models
from django.core.exceptions import ValidationError
from solo.models import SingletonModel
from core.models import StatusModel, SortableModel, Image, File


# ==================== СИНГЛТОН-МОДЕЛИ ДЛЯ СТРАНИЦ ====================

class AboutPage(SingletonModel):
    """
    Страница "О компании" - синглтон.
    """
    
    title = models.CharField(
        max_length=200,
        default="О компании АО «Уголь-Транс»",
        verbose_name="Заголовок страницы"
    )
    
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Meta Title",
        help_text="Для SEO (если пусто, используется заголовок страницы)"
    )
    
    meta_description = models.TextField(
        blank=True,
        verbose_name="Meta Description",
        help_text="Для SEO (макс. 300 символов)"
    )
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Страница 'О компании'"
        verbose_name_plural = "Страница 'О компании'"

    def __str__(self):
        return "Страница 'О компании'"
    
    @property
    def effective_title(self):
        """
        Эффективный заголовок для SEO.
        
        Returns:
            str: Meta Title или заголовок страницы
        """
        return self.meta_title or self.title


class ServicesPage(SingletonModel):
    """
    Страница "Услуги" - синглтон.
    """
    
    title = models.CharField(
        max_length=200,
        default="Услуги АО «Уголь-Транс»",
        verbose_name="Заголовок страницы"
    )
    
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Meta Title"
    )
    
    meta_description = models.TextField(
        blank=True,
        verbose_name="Meta Description",
        help_text="Для SEO (макс. 300 символов)"
    )
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Страница 'Услуги'"
        verbose_name_plural = "Страница 'Услуги'"

    def __str__(self):
        return "Страница 'Услуги'"
    
    @property
    def effective_title(self):
        """
        Эффективный заголовок для SEO.
        
        Returns:
            str: Meta Title или заголовок страницы
        """
        return self.meta_title or self.title


class DocumentsPage(SingletonModel):
    """
    Страница "Документы" - синглтон.
    """
    
    title = models.CharField(
        max_length=200,
        default="Документы АО «Уголь-Транс»",
        verbose_name="Заголовок страницы"
    )
    
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Meta Title"
    )
    
    meta_description = models.TextField(
        blank=True,
        verbose_name="Meta Description",
        help_text="Для SEO (макс. 300 символов)"
    )
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Страница 'Документы'"
        verbose_name_plural = "Страница 'Документы'"

    def __str__(self):
        return "Страница 'Документы'"
    
    @property
    def effective_title(self):
        """
        Эффективный заголовок для SEO.
        
        Returns:
            str: Meta Title или заголовок страницы
        """
        return self.meta_title or self.title


# ==================== МОДЕЛИ СЕКЦИЙ ====================

class AboutSection(StatusModel, SortableModel):
    """
    Секции для страницы 'О компании'.
    """
    
    about_page = models.ForeignKey(
        AboutPage,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name="Страница 'О компании'"
    )
    
    menu_title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Название в меню",
        help_text="Если пусто - не показывается в меню"
    )
    
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Заголовок секции"
    )
    
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="Подзаголовок"
    )
    
    content = models.TextField(
        blank=True,
        verbose_name="Текст"
    )
    
    layout = models.CharField(
        max_length=20,
        choices=[
            ('layout_1', 'Текст → Masonry → Документы'),
            ('layout_2', 'Masonry → Текст → Документы'),
            ('layout_3', 'Masonry | Текст → Документы'),
            ('layout_4', 'Текст | Masonry → Документы'),
        ],
        default='layout_1',
        verbose_name="Макет отображения"
    )

    class Meta:
        verbose_name = "Секция 'О компании'"
        verbose_name_plural = "Секции 'О компании'"
        ordering = ['order']

    def __str__(self):
        return self.title or self.menu_title or f"Секция #{self.id}"
    
    @property
    def display_title(self):
        """
        Заголовок для отображения.
        
        Returns:
            str: Заголовок или название в меню
        """
        return self.title or self.menu_title or "Без названия"
    
    @property
    def images_count(self):
        """
        Количество изображений в секции.
        
        Returns:
            int: Количество изображений
        """
        return self.images.count()
    
    @property
    def files_count(self):
        """
        Количество файлов в секции.
        
        Returns:
            int: Количество файлов
        """
        return self.files.count()


class ServiceSection(StatusModel, SortableModel):
    """
    Секции для страницы 'Услуги'.
    """
    
    services_page = models.ForeignKey(
        ServicesPage,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name="Страница 'Услуги'"
    )
    
    menu_title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Название в меню",
        help_text="Если пусто - не показывается в меню"
    )
    
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Заголовок секции"
    )
    
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="Подзаголовок"
    )
    
    content = models.TextField(
        blank=True,
        verbose_name="Текст"
    )
    
    layout = models.CharField(
        max_length=20,
        choices=[
            ('layout_1', 'Текст → Masonry → Документы'),
            ('layout_2', 'Masonry → Текст → Документы'),
            ('layout_3', 'Masonry | Текст → Документы'),
            ('layout_4', 'Текст | Masonry → Документы'),
        ],
        default='layout_1',
        verbose_name="Макет отображения"
    )

    class Meta:
        verbose_name = "Секция 'Услуги'"
        verbose_name_plural = "Секции 'Услуги'"
        ordering = ['order']

    def __str__(self):
        return self.title or self.menu_title or f"Секция #{self.id}"
    
    @property
    def display_title(self):
        """
        Заголовок для отображения.
        
        Returns:
            str: Заголовок или название в меню
        """
        return self.title or self.menu_title or "Без названия"
    
    @property
    def images_count(self):
        """
        Количество изображений в секции.
        
        Returns:
            int: Количество изображений
        """
        return self.images.count()
    
    @property
    def files_count(self):
        """
        Количество файлов в секции.
        
        Returns:
            int: Количество файлов
        """
        return self.files.count()


class DocumentSection(StatusModel, SortableModel):
    """
    Секции для страницы 'Документы'.
    """
    
    documents_page = models.ForeignKey(
        DocumentsPage,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name="Страница 'Документы'"
    )
    
    menu_title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Название в меню",
        help_text="Если пусто - не показывается в меню"
    )
    
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Заголовок секции"
    )
    
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="Подзаголовок"
    )
    
    content = models.TextField(
        blank=True,
        verbose_name="Текст"
    )
    
    layout = models.CharField(
        max_length=20,
        choices=[
            ('layout_1', 'Текст → Masonry → Документы'),
            ('layout_2', 'Masonry → Текст → Документы'),
            ('layout_3', 'Masonry | Текст → Документы'),
            ('layout_4', 'Текст | Masonry → Документы'),
        ],
        default='layout_1',
        verbose_name="Макет отображения"
    )

    class Meta:
        verbose_name = "Секция 'Документы'"
        verbose_name_plural = "Секции 'Документы'"
        ordering = ['order']

    def __str__(self):
        return self.title or self.menu_title or f"Секция #{self.id}"
    
    @property
    def display_title(self):
        """
        Заголовок для отображения.
        
        Returns:
            str: Заголовок или название в меню
        """
        return self.title or self.menu_title or "Без названия"
    
    @property
    def images_count(self):
        """
        Количество изображений в секции.
        
        Returns:
            int: Количество изображений
        """
        return self.images.count()
    
    @property
    def files_count(self):
        """
        Количество файлов в секции.
        
        Returns:
            int: Количество файлов
        """
        return self.files.count()


# ==================== ОБЩИЕ МОДЕЛИ ДЛЯ МЕДИА ====================

class SectionImage(SortableModel):
    """
    Изображения для секций.
    """
    
    about_section = models.ForeignKey(
        AboutSection,
        on_delete=models.CASCADE,
        related_name='images',
        null=True,
        blank=True,
        verbose_name="Секция 'О компании'"
    )
    
    service_section = models.ForeignKey(
        ServiceSection,
        on_delete=models.CASCADE,
        related_name='images',
        null=True,
        blank=True,
        verbose_name="Секция 'Услуги'"
    )
    
    document_section = models.ForeignKey(
        DocumentSection,
        on_delete=models.CASCADE,
        related_name='images',
        null=True,
        blank=True,
        verbose_name="Секция 'Документы'"
    )
    
    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        verbose_name="Изображение"
    )
    
    class Meta:
        verbose_name = "Изображение секции"
        verbose_name_plural = "Изображения секций"
        ordering = ['order']
        
    def clean(self):
        """
        Проверяем, что изображение привязано только к одной секции.
        """
        sections = [self.about_section, self.service_section, self.document_section]
        filled_sections = [s for s in sections if s is not None]
        
        if len(filled_sections) != 1:
            raise ValidationError("Изображение должно быть привязано ровно к одной секции")
    
    def get_section(self):
        """
        Получаем связанную секцию.
        
        Returns:
            Model или None: Связанная секция
        """
        if self.about_section:
            return self.about_section
        elif self.service_section:
            return self.service_section
        elif self.document_section:
            return self.document_section
        return None

    def get_page_type(self):
        """
        Получаем тип страницы секции.
        
        Returns:
            str: Тип страницы
        """
        section = self.get_section()
        if section:
            if self.about_section:
                return 'about'
            elif self.service_section:
                return 'services'
            elif self.document_section:
                return 'documents'
        return None
    
    @property
    def section_display(self):
        """
        Отображаемое название секции.
        
        Returns:
            str: Название секции
        """
        section = self.get_section()
        return str(section) if section else "—"
    
    @property
    def image_url(self):
        """
        URL изображения.
        
        Returns:
            str или None: URL изображения
        """
        if self.image and self.image.image:
            return self.image.image.url
        return None

    def __str__(self):
        section = self.get_section()
        if section:
            return f"Изображение для {section}"
        return f"Изображение #{self.id}"


class SectionFile(SortableModel):
    """
    Файлы для секций.
    """
    
    about_section = models.ForeignKey(
        AboutSection,
        on_delete=models.CASCADE,
        related_name='files',
        null=True,
        blank=True,
        verbose_name="Секция 'О компании'"
    )
    
    service_section = models.ForeignKey(
        ServiceSection,
        on_delete=models.CASCADE,
        related_name='files',
        null=True,
        blank=True,
        verbose_name="Секция 'Услуги'"
    )
    
    document_section = models.ForeignKey(
        DocumentSection,
        on_delete=models.CASCADE,
        related_name='files',
        null=True,
        blank=True,
        verbose_name="Секция 'Документы'"
    )
    
    file = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        verbose_name="Файл"
    )
    
    class Meta:
        verbose_name = "Файл секции"
        verbose_name_plural = "Файлы секций"
        ordering = ['order']
        
    def clean(self):
        """
        Проверяем, что файл привязан только к одной секции.
        """
        sections = [self.about_section, self.service_section, self.document_section]
        filled_sections = [s for s in sections if s is not None]
        
        if len(filled_sections) != 1:
            raise ValidationError("Файл должен быть привязан ровно к одной секции")
    
    def get_section(self):
        """
        Получаем связанную секцию.
        
        Returns:
            Model или None: Связанная секция
        """
        if self.about_section:
            return self.about_section
        elif self.service_section:
            return self.service_section
        elif self.document_section:
            return self.document_section
        return None

    def get_page_type(self):
        """
        Получаем тип страницы секции.
        
        Returns:
            str: Тип страницы
        """
        section = self.get_section()
        if section:
            if self.about_section:
                return 'about'
            elif self.service_section:
                return 'services'
            elif self.document_section:
                return 'documents'
        return None
    
    @property
    def section_display(self):
        """
        Отображаемое название секции.
        
        Returns:
            str: Название секции
        """
        section = self.get_section()
        return str(section) if section else "—"
    
    @property
    def file_size_display(self):
        """
        Отображаем размер файла в читаемом формате.
        
        Returns:
            str: Размер файла
        """
        if self.file and self.file.file:
            size = self.file.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            elif size < 1024 * 1024 * 1024:
                return f"{size / (1024 * 1024):.1f} MB"
            else:
                return f"{size / (1024 * 1024 * 1024):.1f} GB"
        return "—"
    
    @property
    def file_extension(self):
        """
        Получаем расширение файла.
        
        Returns:
            str: Расширение файла
        """
        if self.file and self.file.file:
            file_name = self.file.file.name
            return file_name.split('.')[-1].upper() if '.' in file_name else 'НЕТ'
        return "—"
    
    @property
    def file_name(self):
        """
        Имя файла.
        
        Returns:
            str: Имя файла
        """
        if self.file:
            return self.file.name
        return ""
    
    @property
    def file_url(self):
        """
        URL файла.
        
        Returns:
            str или None: URL файла
        """
        if self.file and self.file.file:
            return self.file.file.url
        return None

    def __str__(self):
        section = self.get_section()
        if section:
            return f"Файл для {section}"
        return f"Файл #{self.id}"