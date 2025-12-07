from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminBase
from .models import News, NewsImage, NewsFile
from core.mixins import InlineAccessMixin, ContentManagerAccessMixin


# ==================== КАСТОМНЫЕ ФИЛЬТРЫ ====================

class PublicationStatusFilter(admin.SimpleListFilter):
    """Фильтр по статусу публикации."""
    title = 'Статус публикации'
    parameter_name = 'publication_status'
    
    def lookups(self, request, model_admin):
        return (
            ('draft', '⚫ Черновики'),
            ('scheduled', '🟠 Запланированные'),
            ('published', '🟢 Опубликованные'),
        )
    
    def queryset(self, request, queryset):
        now = timezone.now()
        
        if self.value() == 'draft':
            return queryset.filter(is_active=False)
        
        elif self.value() == 'scheduled':
            return queryset.filter(is_active=True, publish_date__gt=now)
        
        elif self.value() == 'published':
            return queryset.filter(is_active=True, publish_date__lte=now)
        
        return queryset


class PublicationDateFilter(admin.SimpleListFilter):
    """Фильтр по дате публикации."""
    title = 'Дата публикации'
    parameter_name = 'pub_date'
    
    def lookups(self, request, model_admin):
        return (
            ('today', 'Сегодня'),
            ('week', 'Эта неделя'),
            ('month', 'Этот месяц'),
            ('future', 'Запланированные'),
            ('past', 'Прошлые'),
        )
    
    def queryset(self, request, queryset):
        now = timezone.now()
        
        if self.value() == 'today':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return queryset.filter(publish_date__gte=today_start)
        
        elif self.value() == 'week':
            week_ago = now - timedelta(days=7)
            return queryset.filter(publish_date__gte=week_ago)
        
        elif self.value() == 'month':
            month_ago = now - timedelta(days=30)
            return queryset.filter(publish_date__gte=month_ago)
        
        elif self.value() == 'future':
            return queryset.filter(publish_date__gt=now)
        
        elif self.value() == 'past':
            return queryset.filter(publish_date__lte=now)
        
        return queryset


# ==================== INLINE ФОРМЫ ====================

class NewsImageForm(forms.ModelForm):
    class Meta:
        model = NewsImage
        fields = '__all__'
        widgets = {
            'order': forms.HiddenInput(),
        }


class NewsImageInline(InlineAccessMixin, SortableInlineAdminMixin, admin.TabularInline):
    model = NewsImage
    form = NewsImageForm
    extra = 0
    fields = ['order', 'image']
    sortable_field_name = 'order'
    
    def order_display(self, obj):
        if obj and obj.pk:
            return obj.order
        return '—'
    order_display.short_description = 'Порядок'


class NewsFileForm(forms.ModelForm):
    class Meta:
        model = NewsFile
        fields = '__all__'
        widgets = {
            'order': forms.HiddenInput(),
        }


class NewsFileInline(InlineAccessMixin, SortableInlineAdminMixin, admin.TabularInline):
    model = NewsFile
    form = NewsFileForm
    extra = 0
    fields = ['order', 'file', 'file_name', 'file_type', 'file_size']
    readonly_fields = ('file_name', 'file_type', 'file_size')
    sortable_field_name = 'order'
    
    def file_name(self, obj):
        """Имя файла."""
        if obj.file and obj.file.name:
            return obj.file.name[:30] + "..." if len(obj.file.name) > 30 else obj.file.name
        return "—"
    file_name.short_description = 'Имя файла'
    
    def file_type(self, obj):
        """Тип файла."""
        if obj.file and obj.file.extension:
            return obj.file.extension
        return "—"
    file_type.short_description = 'Тип'
    
    def file_size(self, obj):
        """Размер файла."""
        if obj.file and obj.file.size_display:
            return obj.file.size_display
        return "—"
    file_size.short_description = 'Размер'


# ==================== ОСНОВНАЯ АДМИНКА ====================

class NewsAdminForm(forms.ModelForm):
    """Форма для новости."""
    class Meta:
        model = News
        fields = '__all__'
        widgets = {
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'rows': 10}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем крестик удаления у главного изображения
        if 'main_image' in self.fields:
            self.fields['main_image'].widget.can_delete_related = False
            self.fields['main_image'].widget.can_change_related = True
            self.fields['main_image'].widget.can_view_related = True
            self.fields['main_image'].widget.can_add_related = True


@admin.register(News)
class NewsAdmin(ContentManagerAccessMixin, SortableAdminBase, admin.ModelAdmin):
    form = NewsAdminForm

    # ✏️ ПЕРВЫЙ СТОЛБЕЦ - ИЗМЕНИТЬ
    list_display = (
        'edit_link',
        'title_display',
        'is_active_display',
        'publication_status_display',
        'publish_date_formatted',
        'short_description_preview',
    )
    
    list_filter = (
        PublicationStatusFilter,
        PublicationDateFilter,
        'is_active',
        'created_at',
    )
    
    search_fields = ('title', 'short_description', 'content')
    
    readonly_fields = (
        'created_at',
        'updated_at',
        'slug_display',
        'current_publication_status',  # Добавлено поле текущего статуса
    )
    
    prepopulated_fields = {'slug': ('title',)}
    
    list_per_page = 30

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'title',
                'slug',
                'short_description',
                'main_image',
                'content',
                'publish_date',
            )
        }),
        ('Статус', {
            'fields': ('is_active', 'current_publication_status')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at', 'slug_display'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [NewsImageInline, NewsFileInline]
    
    # ==================== КОЛОНКА "ИЗМЕНИТЬ" ====================
    def edit_link(self, obj):
        """Ссылка на редактирование в виде текста с карандашиком."""
        url = reverse('admin:news_news_change', args=[obj.id])
        return format_html(
            '<a href="{}" style="text-decoration: none; color: #447e9b;" title="Редактировать">'
            '<span style="font-size: 14px;">✏️</span> Изменить'
            '</a>',
            url
        )
    edit_link.short_description = ''
    edit_link.admin_order_field = 'id'
    
    def title_display(self, obj):
        """Заголовок БЕЗ ссылки."""
        return obj.title
    title_display.short_description = 'Заголовок'
    title_display.admin_order_field = 'title'
    
    def is_active_display(self, obj):
        """Активность ✅/❌."""
        if obj.is_active:
            return "✅"
        else:
            return "❌"
    is_active_display.short_description = 'Активна'
    is_active_display.admin_order_field = 'is_active'
    
    def publication_status_display(self, obj):
        """Цветной бейдж статуса публикации."""
        status = obj.publication_status
        color = obj.publication_status_color
        
        return format_html(
            '<span style="color: {}; font-weight: bold; padding: 3px 8px; '
            'border-radius: 3px; background-color: {}20;">{}</span>',
            color,
            color,
            status
        )
    publication_status_display.short_description = 'Статус'
    publication_status_display.admin_order_field = 'publish_date'
    
    def publish_date_formatted(self, obj):
        """Форматированная дата публикации."""
        return obj.publish_date.strftime('%d.%m.%Y %H:%M')
    publish_date_formatted.short_description = 'Дата публикации'
    publish_date_formatted.admin_order_field = 'publish_date'
    
    def short_description_preview(self, obj):
        """Превью короткого описания."""
        if obj.short_description:
            preview = obj.short_description[:50] + "..." if len(obj.short_description) > 50 else obj.short_description
            return format_html(
                '<span title="{}">{}</span>',
                obj.short_description,
                preview
            )
        return "—"
    short_description_preview.short_description = 'Описание'
    
    def slug_display(self, obj):
        """Отображение slug (только для просмотра)."""
        return format_html(
            '<code style="background: #f5f5f5; padding: 3px 6px; border-radius: 3px;">{}</code>',
            obj.slug
        )
    slug_display.short_description = 'URL-адрес'
    
    def current_publication_status(self, obj):
        """Текущий статус публикации (только для просмотра)."""
        return obj.publication_status
    current_publication_status.short_description = 'Текущий статус'
    
    # ==================== ОПТИМИЗАЦИЯ ====================
    
    def get_queryset(self, request):
        """Оптимизированный queryset."""
        return super().get_queryset(request).select_related('main_image').order_by('-publish_date')