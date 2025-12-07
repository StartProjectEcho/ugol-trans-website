from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from core.models import StatusModel, SortableModel, Image


# ==================== SINGLETON МОДЕЛИ (один экземпляр) ====================

class HeroBlock(StatusModel):
    """
    Приветственный блок (верхний баннер) на главной странице.
    """
    
    background_image = models.ForeignKey(
        Image,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Фоновое изображение"),
        related_name='hero_backgrounds'
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_("Заголовок"),
        blank=True,
        help_text=_("Основной заголовок баннера")
    )
    
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_("Подзаголовок")
    )
    
    cta_button_text = models.CharField(
        max_length=50,
        default=_("Связаться с нами"),
        verbose_name=_("Текст кнопки")
    )
    
    show_news_carousel = models.BooleanField(
        default=True,
        verbose_name=_("Показывать карусель новостей"),
        help_text=_("Отображать карусель с последними новостями")
    )
    
    news_count = models.PositiveIntegerField(
        default=5,
        verbose_name=_("Количество новостей"),
        help_text=_("Сколько последних новостей показывать в карусели"),
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    
    class Meta:
        verbose_name = "Приветственный блок"
        verbose_name_plural = "Приветственный блок"
    
    def __str__(self):
        return "Приветственный блок"
    
    def get_news_for_carousel(self):
        """
        Получает новости для карусели.
        
        Returns:
            QuerySet: QuerySet с новостями
        """
        if not self.show_news_carousel:
            return []
        
        from news.models import News
        news_qs = News.objects.filter(is_active=True)
        
        # Всегда показываем последние N новостей
        return news_qs.order_by('-publish_date')[:self.news_count]
    
    def clean(self):
        """
        Валидация данных.
        """
        super().clean()
        
        # Если карусель отключена, сбрасываем количество новостей
        if not self.show_news_carousel and self.news_count != 5:
            self.news_count = 5


class AboutBlock(StatusModel):
    """
    Блок 'О компании' на главной странице.
    """
    
    title = models.CharField(
        max_length=200,
        verbose_name=_("Заголовок"),
        blank=True
    )
    
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_("Подзаголовок")
    )
    
    content = models.TextField(
        verbose_name=_("Текст"),
        blank=True,
    )
    
    class Meta:
        verbose_name = "Блок 'О компании'"
        verbose_name_plural = "Блок 'О компании'"
    
    def __str__(self):
        return "Блок 'О компании'"


class AdvantageBlock(StatusModel):
    """
    Заголовок для раздела преимуществ компании.
    """
    
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Заголовок")
    )
    
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_("Подзаголовок")
    )
    
    content = models.TextField(
        blank=True,
        verbose_name=_("Текст")
    )
    
    class Meta:
        verbose_name = "Блок 'Преимущества'"
        verbose_name_plural = "Блок 'Преимущества'"
    
    def __str__(self):
        return "Блок 'Преимущества'"


class AnalyticsBlock(StatusModel):
    """
    Заголовок для раздела с диаграммами.
    """
    
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Заголовок")
    )
    
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_("Подзаголовок")
    )
    
    content = models.TextField(
        blank=True,
        verbose_name=_("Текст")
    )
    
    # Связь с диаграммами из приложения business_analytics
    diagram_1 = models.ForeignKey(
        'business_analytics.Diagram',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analytics_block_1',
        verbose_name=_("Первая диаграмма"),
        help_text=_("Выберите диаграмму из раздела Бизнес-аналитика")
    )
    
    diagram_2 = models.ForeignKey(
        'business_analytics.Diagram',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analytics_block_2',
        verbose_name=_("Вторая диаграмма"),
        help_text=_("Выберите диаграмму из раздела Бизнес-аналитика")
    )
    
    class Meta:
        verbose_name = "Блок 'Бизнес-аналитика'"
        verbose_name_plural = "Блоки 'Бизнес-аналитика'"
    
    def __str__(self):
        return "Блок 'Бизнес-аналитика'"
    
    def clean(self):
        """
        Валидация данных.
        """
        super().clean()
        
        # Проверяем, что не выбрана одна и та же диаграмма дважды
        if self.diagram_1 and self.diagram_2 and self.diagram_1 == self.diagram_2:
            raise ValidationError({
                'diagram_2': 'Нельзя выбирать одну и ту же диаграмму дважды. Выберите другую диаграмму.'
            })
    
    @property
    def has_diagrams(self):
        """
        Проверяет, выбраны ли диаграммы.
        
        Returns:
            bool: True если выбрана хотя бы одна диаграмма
        """
        return bool(self.diagram_1 or self.diagram_2)


class PartnersBlock(StatusModel):
    """
    Заголовок для карусели партнеров.
    """
    
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Заголовок")
    )
    
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_("Подзаголовок")
    )
    
    content = models.TextField(
        blank=True,
        verbose_name=_("Текст")
    )
    
    class Meta:
        verbose_name = "Блок 'Партнеры'"
        verbose_name_plural = "Блоки 'Партнеры'"
    
    def __str__(self):
        return "Блок 'Партнеры'"


class ContactsBlock(StatusModel):
    """
    Блок контактов с кнопкой CTA.
    """
    
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Заголовок")
    )
    
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_("Подзаголовок")
    )
    
    content = models.TextField(
        blank=True,
        verbose_name=_("Текст")
    )
    
    cta_button_text = models.CharField(
        max_length=50,
        default=_("Перейти к контактам"),
        verbose_name=_("Текст кнопки")
    )
    
    class Meta:
        verbose_name = "Блок 'Контакты'"
        verbose_name_plural = "Блоки 'Контакты'"
    
    def __str__(self):
        return "Блок 'Контакты'"


# ==================== МОДЕЛИ С МНОЖЕСТВОМ ЗАПИСЕЙ ====================

class Advantage(StatusModel, SortableModel):
    """
    Элементы списка преимуществ с иконками.
    """
    
    advantage_block = models.ForeignKey(
        AdvantageBlock,
        on_delete=models.CASCADE,
        related_name='advantages',
        verbose_name=_("Блок преимуществ"),
        help_text=_("Родительский блок преимуществ")
    )
    
    icon = models.ForeignKey(
        Image,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_("Иконка"),
        related_name='advantage_icons'
    )
    
    title = models.CharField(
        max_length=100,
        verbose_name=_("Заголовок")
    )
    
    description = models.CharField(
        max_length=300,
        verbose_name=_("Описание")
    )
    
    class Meta:
        verbose_name = "Преимущество"
        verbose_name_plural = "Преимущества"
        ordering = ['order']
    
    def __str__(self):
        return self.title
    
    @property
    def icon_url(self):
        """
        URL иконки.
        
        Returns:
            str или None: URL иконки
        """
        if self.icon and self.icon.image:
            return self.icon.image.url
        return None


class Partner(StatusModel, SortableModel):
    """
    Элементы карусели логотипов партнеров.
    """
    
    partners_block = models.ForeignKey(
        PartnersBlock,
        on_delete=models.CASCADE,
        related_name='partners',
        verbose_name=_("Блок партнеров"),
        help_text=_("Родительский блок партнеров")
    )
    
    logo = models.ForeignKey(
        Image,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("Логотип партнера"),
        related_name='partner_logos'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_("Название компании")
    )
    
    website = models.URLField(
        blank=True,
        verbose_name=_("Сайт партнера")
    )
    
    class Meta:
        verbose_name = "Партнер"
        verbose_name_plural = "Партнеры"
        ordering = ['order']
    
    def __str__(self):
        return self.name
    
    @property
    def logo_url(self):
        """
        URL логотипа.
        
        Returns:
            str или None: URL логотипа
        """
        if self.logo and self.logo.image:
            return self.logo.image.url
        return None
    
    @property
    def domain(self):
        """
        Домен сайта партнера.
        
        Returns:
            str: Домен
        """
        if self.website:
            from urllib.parse import urlparse
            parsed = urlparse(self.website)
            return parsed.netloc
        return ""