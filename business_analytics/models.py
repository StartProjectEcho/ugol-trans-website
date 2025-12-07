from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models import Sum
from core.models import StatusModel, SortableModel
import re
from django.utils.html import format_html


class Diagram(StatusModel, SortableModel):
    """
    Модель диаграммы для бизнес-аналитики.
    """
    MAX_ACTIVE_DIAGRAMS = 2
    CHART_TYPES = [
        ('column', '📊 Столбчатая'),
        ('pie', '🥧 Круговая'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name="Название диаграммы"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    chart_type = models.CharField(
        max_length=10,
        choices=CHART_TYPES,
        default='column',
        verbose_name="Тип диаграммы"
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name="Единица измерения"
    )

    class Meta:
        verbose_name = "Диаграмма"
        verbose_name_plural = "Диаграммы"
        ordering = ['order']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['order']),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        """
        Валидация данных диаграммы.
        """
        super().clean()
        self._validate_active_limit()
        self._validate_measurement_unit()
    
    def _validate_active_limit(self):
        """
        Валидация лимита активных диаграмм.
        """
        if self.is_active:
            active_qs = Diagram.objects.filter(is_active=True)
            if self.pk:
                active_qs = active_qs.exclude(pk=self.pk)
            
            if active_qs.count() >= self.MAX_ACTIVE_DIAGRAMS:
                raise ValidationError({
                    'is_active': f'Нельзя активировать более {self.MAX_ACTIVE_DIAGRAMS} диаграмм. '
                               f'Сейчас активно: {active_qs.count()}. '
                               f'Сначала деактивируйте одну из активных диаграмм.'
                })
    
    def _validate_measurement_unit(self):
        """
        Валидация единицы измерения.
        """
        if not self.measurement_unit or self.measurement_unit.strip() == '':
            raise ValidationError({
                'measurement_unit': 'Единица измерения обязательна для заполнения.'
            })
    
    def get_total_value(self):
        """
        Сумма всех категорий диаграммы.
        """
        result = self.categories.aggregate(total=Sum('value'))
        return result['total'] or 0.0
    
    @property
    def active_categories(self):
        """
        Активные категории диаграммы.
        """
        return self.categories.all()
    
    @property
    def chart_type_display(self):
        """
        Отображаемое название типа диаграммы.
        """
        return dict(self.CHART_TYPES).get(self.chart_type, self.chart_type)
    
    @property
    def is_max_active_reached(self):
        """
        Проверяет, достигнут ли лимит активных диаграмм.
        """
        active_count = Diagram.objects.filter(is_active=True).count()
        if self.pk and self.is_active:
            active_count -= 1
        return active_count >= self.MAX_ACTIVE_DIAGRAMS
    
    def get_chart_preview_html(self):
        """
        HTML превью диаграммы (упрощенное).
        """
        categories = self.categories.all()[:5]  # Берем первые 5
        
        if not categories:
            return format_html('<div style="padding: 20px; background: #f8f9fa; color: #999; text-align: center;">Нет данных</div>')
        
        # Простое текстовое представление
        preview = []
        for cat in categories:
            preview.append(f"{cat.name}: {cat.value}")
        
        return format_html('<br>'.join(preview))
    
    def get_status_display_formatted(self):
        """
        Форматированное отображение статуса.
        """
        if self.is_active:
            return "✅"
        else:
            return "❌"


class DiagramCategory(SortableModel):
    """
    Модель категории диаграммы.
    """
    diagram = models.ForeignKey(
        Diagram,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name="Диаграмма"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Название категории"
    )
    value = models.FloatField(
        verbose_name="Числовое значение",
        validators=[MinValueValidator(0.0)],
        help_text="Неотрицательное число"
    )
    color = models.CharField(
        max_length=7,
        default="#FF009D",
        verbose_name="Цвет в HEX",
        help_text="Например: #4CAF50 (зеленый)"
    )

    class Meta:
        verbose_name = "Категория диаграммы"
        verbose_name_plural = "Категории диаграммы"
        ordering = ['order']
        indexes = [
            models.Index(fields=['diagram', 'order']),
        ]

    def __str__(self):
        return f"{self.name} ({self.diagram.title})"

    def clean(self):
        """
        Валидация данных категории.
        """
        super().clean()
        self._validate_color()
    
    def _validate_color(self):
        """
        Валидация цвета.
        """
        # Проверка HEX формата
        color_pattern = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
        if not color_pattern.match(self.color):
            raise ValidationError({
                'color': "Неверный формат цвета. Используйте HEX-формат: #FFFFFF или #FFF"
            })
        
        # Нормализация
        if len(self.color) == 4:  # #RGB -> #RRGGBB
            self.color = f"#{self.color[1]}{self.color[1]}{self.color[2]}{self.color[2]}{self.color[3]}{self.color[3]}"
        
        self.color = self.color.upper()
    
    def get_percentage(self):
        """
        Расчет процента от общей суммы.
        """
        if not hasattr(self, 'diagram') or not self.diagram:
            return 0.0
        
        total = self.diagram.get_total_value()
        if total == 0:
            return 0.0
        
        return (self.value / total) * 100
    
    @property
    def percentage_display(self):
        """
        Отформатированный процент.
        """
        return f"{self.get_percentage():.1f}%"
    
    @property
    def color_display(self):
        """
        Отображение цвета.
        """
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; '
            'border: 1px solid #ccc; border-radius: 3px;" title="{}"></div>',
            self.color,
            self.color
        )

    def save(self, *args, **kwargs):
        """
        Сохранение с валидацией.
        """
        self.full_clean()
        super().save(*args, **kwargs)