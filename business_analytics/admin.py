from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin
from core.mixins import ContentManagerAccessMixin, InlineAccessMixin
from .models import Diagram, DiagramCategory


# ==================== ФОРМЫ ====================

class DiagramCategoryForm(forms.ModelForm):
    """
    Форма для категории диаграммы.
    """
    class Meta:
        model = DiagramCategory
        fields = '__all__'
        widgets = {
            'color': forms.TextInput(attrs={
                'type': 'color',
                'style': 'width: 100px; height: 30px; padding: 0;'
            }),
            'order': forms.HiddenInput(),
            'value': forms.NumberInput(attrs={'step': '0.1'}),
        }


class DiagramAdminForm(forms.ModelForm):
    """
    Форма для диаграммы.
    """
    class Meta:
        model = Diagram
        fields = '__all__'
        widgets = {
            'order': forms.HiddenInput(),
            'description': forms.Textarea(attrs={'rows': 3}),
            'measurement_unit': forms.TextInput(attrs={
                'placeholder': 'Например: шт., %, руб., тонн'
            }),
        }


# ==================== INLINE КАТЕГОРИЙ ====================

class DiagramCategoryInline(InlineAccessMixin, SortableInlineAdminMixin, admin.TabularInline):
    """
    Inline для категорий диаграммы.
    """
    model = DiagramCategory
    form = DiagramCategoryForm
    extra = 0
    min_num = 0  # Можно создать диаграмму без категорий
    max_num = 10  # Максимум 10 категорий
    fields = ['name', 'value', 'color', 'order', 'preview']
    readonly_fields = ['preview']
    sortable_field_name = 'order'
    
    def preview(self, obj):
        """
        Превью категории с цветом и процентом.
        """
        if obj and obj.pk:
            return format_html(
                '''
                <div style="display: flex; align-items: center; gap: 10px; padding: 5px; background: #f8f9fa; border-radius: 4px;">
                    <div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>
                    <div>
                        <div><strong>{}</strong></div>
                        <div style="font-size: 12px; color: #666;">{}</div>
                    </div>
                </div>
                ''',
                obj.color,
                obj.percentage_display,
                f"{obj.value} {obj.diagram.measurement_unit if hasattr(obj, 'diagram') and obj.diagram else ''}"
            )
        return "—"
    preview.short_description = 'Превью'


# ==================== АДМИНКА ДЛЯ ДИАГРАММ ====================

@admin.register(Diagram)
class DiagramAdmin(ContentManagerAccessMixin, SortableAdminBase, admin.ModelAdmin):
    """
    Админка для диаграмм. Доступна только админам и контент-менеджерам.
    """
    form = DiagramAdminForm
    
    # ✏️ ПЕРВЫЙ СТОЛБЕЦ - ИЗМЕНИТЬ
    list_display = (
        'edit_link',
        'title_display',
        'status_display',
        'chart_type_display',
        'measurement_unit_display',
        'categories_count_display',
        'total_value_display',
        'created_at_display',
    )
    
    list_filter = ('is_active', 'chart_type')
    search_fields = ('title', 'description', 'measurement_unit')
    list_per_page = 25
    sortable_field_name = 'order'
    
    # Сортировка: сначала активные, потом по дате создания (новые выше)
    ordering = ('-is_active', '-created_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'title',
                'description',
                'chart_type',
                'measurement_unit',
                'order',
            )
        }),
        ('Статус', {
            'fields': ('is_active',),
        }),
    )
    
    inlines = [DiagramCategoryInline]
    
    # ==================== КОЛОНКА "ИЗМЕНИТЬ" ====================
    def edit_link(self, obj):
        """Ссылка на редактирование в виде текста с карандашиком."""
        url = reverse('admin:business_analytics_diagram_change', args=[obj.id])
        return format_html(
            '<a href="{}" style="text-decoration: none; color: #447e9b;" title="Редактировать">'
            '<span style="font-size: 14px;">✏️</span> Изменить'
            '</a>',
            url
        )
    edit_link.short_description = ''
    edit_link.admin_order_field = 'id'
    
    def title_display(self, obj):
        """Название диаграммы БЕЗ ссылки."""
        return obj.title
    title_display.short_description = 'Название'
    title_display.admin_order_field = 'title'
    
    def status_display(self, obj):
        """Отображение статуса активности."""
        if obj.is_active:
            return format_html(
                '<span style="color: #32CD32; font-weight: bold;">✅</span>'
            )
        else:
            return format_html(
                '<span style="color: #DC143C; font-weight: bold;">❌</span>'
            )
    status_display.short_description = 'Активность'
    status_display.admin_order_field = 'is_active'
    
    def chart_type_display(self, obj):
        """Отображение типа диаграммы."""
        return obj.chart_type_display
    chart_type_display.short_description = 'Тип'
    chart_type_display.admin_order_field = 'chart_type'
    
    def measurement_unit_display(self, obj):
        """Отображение единицы измерения."""
        return obj.measurement_unit or '—'
    measurement_unit_display.short_description = 'Ед. изм.'
    measurement_unit_display.admin_order_field = 'measurement_unit'
    
    def categories_count_display(self, obj):
        """Количество категорий с цветовой индикацией."""
        count = obj.categories.count()
        if count == 0:
            return format_html('<span style="color: #DC143C; font-weight: bold;">{}</span>', "0")
        elif count < 3:
            return format_html('<span style="color: #FFA500;">{}</span>', f"{count}")
        else:
            return format_html('<span style="color: #32CD32; font-weight: bold;">{}</span>', f"{count}")
    categories_count_display.short_description = 'Категории'
    
    def total_value_display(self, obj):
        """Общая сумма значений."""
        total = obj.get_total_value()
        unit = obj.measurement_unit if obj.measurement_unit else ''
        return f"{total:.1f} {unit}"
    total_value_display.short_description = 'Сумма'
    
    def created_at_display(self, obj):
        """Отображение даты создания в удобном формате."""
        if obj.created_at:
            return obj.created_at.strftime("%d.%m.%Y %H:%M")
        return "—"
    created_at_display.short_description = 'Создано'
    created_at_display.admin_order_field = 'created_at'
    
    # ==================== МАССОВЫЕ ДЕЙСТВИЯ ====================
    
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        """
        Активировать выбранные диаграммы с проверкой лимита.
        """
        active_count = Diagram.objects.filter(is_active=True).count()
        available_slots = Diagram.MAX_ACTIVE_DIAGRAMS - active_count
        
        if available_slots <= 0:
            self.message_user(
                request,
                f'Достигнут лимит в {Diagram.MAX_ACTIVE_DIAGRAMS} активных диаграмм.',
                messages.ERROR
            )
            return
        
        # Берем только неактивные диаграммы
        inactive_diagrams = queryset.filter(is_active=False)
        to_activate = inactive_diagrams[:available_slots]
        
        if not to_activate:
            self.message_user(
                request,
                'Среди выбранных нет неактивных диаграмм.',
                messages.WARNING
            )
            return
        
        updated = 0
        for diagram in to_activate:
            diagram.is_active = True
            diagram.save()
            updated += 1
        
        remaining = available_slots - updated
        message = f'Активировано {updated} диаграмм.'
        if remaining > 0 and inactive_diagrams.count() > available_slots:
            message += f' Можно активировать еще {remaining} диаграмм.'
        
        self.message_user(request, message, messages.SUCCESS)
    make_active.short_description = "✅ Активировать"
    
    def make_inactive(self, request, queryset):
        """Деактивировать выбранные диаграммы."""
        active_diagrams = queryset.filter(is_active=True)
        updated = active_diagrams.update(is_active=False)
        
        if updated > 0:
            self.message_user(
                request,
                f'Деактивировано {updated} диаграмм.',
                messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                'Среди выбранных нет активных диаграмм.',
                messages.WARNING
            )
    make_inactive.short_description = "❌ Деактивировать"
    
    # ==================== ПРЕДПРОСМОТР И ЛИМИТЫ ====================
    
    def changelist_view(self, request, extra_context=None):
        """
        Отображение информации о лимите активных диаграмм.
        """
        extra_context = extra_context or {}
        active_count = Diagram.objects.filter(is_active=True).count()
        extra_context.update({
            'title': f'Диаграммы (активных: {active_count}/{Diagram.MAX_ACTIVE_DIAGRAMS})',
            'active_count': active_count,
            'max_active': Diagram.MAX_ACTIVE_DIAGRAMS,
            'available_slots': Diagram.MAX_ACTIVE_DIAGRAMS - active_count,
        })
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_readonly_fields(self, request, obj=None):
        """
        Поля только для чтения при достижении лимита.
        """
        readonly_fields = list(super().get_readonly_fields(request, obj))
        
        if obj and obj.is_max_active_reached and not obj.is_active:
            # Если лимит достигнут, поле is_active становится readonly
            readonly_fields.append('is_active')
        
        return readonly_fields
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Кастомная форма с подсказками.
        """
        form = super().get_form(request, obj, **kwargs)
        
        if obj and obj.is_max_active_reached and not obj.is_active:
            # Показываем предупреждение если лимит достигнут
            # Безопасная проверка наличия поля is_active в форме
            if 'is_active' in form.base_fields:
                form.base_fields['is_active'].help_text = (
                    f'⚠️ Достигнут лимит активных диаграмм ({Diagram.MAX_ACTIVE_DIAGRAMS}). '
                    'Сначала деактивируйте одну из активных диаграмм.'
                )
        
        return form
    
    # ==================== ОПТИМИЗАЦИЯ ====================
    
    def get_queryset(self, request):
        """
        Оптимизированный queryset.
        """
        from django.db.models import Count, Sum
        return super().get_queryset(request).annotate(
            categories_count=Count('categories'),
            total_value=Sum('categories__value')
        ).select_related()
    
    def save_model(self, request, obj, form, change):
        """
        Сохранение с обработкой ошибок.
        """
        try:
            with transaction.atomic():
                super().save_model(request, obj, form, change)
        except ValidationError as e:
            # Показываем ошибки пользователю
            if hasattr(e, 'message_dict'):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
            else:
                self.message_user(request, str(e), messages.ERROR)
                raise