"""
Админка приложения core.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django import forms
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.conf import settings
from solo.admin import SingletonModelAdmin
from .models import SiteSettings, Image, File
from .mixins import SiteSettingsAccessMixin, ContentManagerAccessMixin


@admin.register(SiteSettings)
class SiteSettingsAdmin(SiteSettingsAccessMixin, SingletonModelAdmin):
    """Админка для настроек сайта."""
    pass


class ImageForm(forms.ModelForm):
    """Форма для модели Image."""
    class Meta:
        model = Image
        fields = '__all__'
    
    def clean(self):
        """Дополнительная валидация изображения."""
        cleaned_data = super().clean()
        
        # Проверка размера файла
        max_size = getattr(settings, 'MAX_IMAGE_SIZE', 10 * 1024 * 1024)
        
        image = cleaned_data.get('image')
        if image and image.size > max_size:
            raise ValidationError({
                'image': f'Размер файла не должен превышать {max_size // (1024*1024)}MB.'
            })
        
        return cleaned_data


class BaseAdminMixin:
    """Общие методы для админки."""
    
    def edit_link(self, obj):
        """Ссылка на редактирование."""
        if obj.id:
            url = reverse(f'admin:core_{self.model._meta.model_name}_change', args=[obj.id])
            return format_html(
                '<a href="{}" style="text-decoration: none; color: #447e9b;" title="Редактировать">'
                '<span style="font-size: 14px;">✏️</span> Изменить'
                '</a>',
                url
            )
        return "—"
    edit_link.short_description = ""
    edit_link.admin_order_field = 'id'
    
    def created_at_formatted(self, obj):
        """Форматированная дата создания."""
        return obj.created_at.strftime('%d.%m.%Y')
    created_at_formatted.short_description = "Создан"
    created_at_formatted.admin_order_field = 'created_at'
    
    def is_active_boolean(self, obj):
        """Отображение статуса активности."""
        return "✅" if obj.is_active else "❌"
    is_active_boolean.short_description = "Активно"
    is_active_boolean.admin_order_field = 'is_active'
    
    def make_active(self, request, queryset):
        """Активировать выбранные объекты."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, 
            f'Активировано объектов: {updated}', 
            messages.SUCCESS
        )
    make_active.short_description = "✅ Активировать"
    
    def make_inactive(self, request, queryset):
        """Деактивировать выбранные объекты."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, 
            f'Деактивировано объектов: {updated}', 
            messages.SUCCESS
        )
    make_inactive.short_description = "❌ Деактивировать"


@admin.register(Image)
class ImageAdmin(ContentManagerAccessMixin, BaseAdminMixin, admin.ModelAdmin):
    """Админка для изображений."""
    form = ImageForm
    
    list_display = (
        'edit_link',
        'preview_small', 
        'alt_text_display',
        'size_display',
        'width_height',
        'file_exists_badge',
        'is_active_boolean',
        'created_at_formatted'
    )
    
    list_filter = ('is_active', 'created_at')
    search_fields = ('alt_text', 'image')
    readonly_fields = (
        'created_at', 
        'updated_at', 
        'preview_large',
        'size_display',
        'filename_display',
        'width_height',
        'recommended_usage_display',
        'file_exists_status'
    )
    list_per_page = 25
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('image', 'preview_large', 'alt_text')
        }),
        ('Статус', {
            'fields': ('is_active', 'file_exists_status')
        }),
        ('Техническая информация', {
            'fields': ('filename_display', 'size_display', 'width_height', 'recommended_usage_display'),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    class Media:
        css = {
            'all': ('admin/css/core.css',)
        }
        js = ('admin/js/image_preview.js',)
    
    def preview_small(self, obj):
        """Маленькое превью изображения в списке."""
        if obj.url and obj.file_exists():
            change_url = reverse('admin:core_image_change', args=[obj.id])
            return format_html(
                '''
                <div class="image-preview-small">
                    <a href="{}">
                        <img src="{}" class="thumbnail" title="Нажмите для редактирования" />
                    </a>
                </div>
                ''', 
                change_url,
                obj.url
            )
        elif obj.url:
            # Файл не найден, но есть запись в БД
            return format_html('<div class="no-image" title="Файл не найден на диске">⚠️</div>')
        return format_html('<div class="no-image">Нет</div>')
    preview_small.short_description = "Превью"
    preview_small.admin_order_field = 'image'
    
    def alt_text_display(self, obj):
        """ALT текст."""
        if obj.alt_text:
            display_text = obj.alt_text[:50] + '...' if len(obj.alt_text) > 50 else obj.alt_text
            return format_html(
                '<span title="{}">{}</span>',
                obj.alt_text,
                display_text
            )
        return "—"
    alt_text_display.short_description = "Alt текст"
    alt_text_display.admin_order_field = 'alt_text'
    
    def size_display(self, obj):
        """Отображение размера файла."""
        return obj.size_display
    size_display.short_description = "Размер"
    
    def width_height(self, obj):
        """Отображение размеров изображения."""
        return obj.width_height
    width_height.short_description = "Размеры"
    
    def file_exists_badge(self, obj):
        """Бейдж статуса файла."""
        if obj.file_exists():
            return format_html('<span style="color: green;">✓ Файл найден</span>')
        elif obj.url:
            return format_html('<span style="color: red;" title="Файл отсутствует на диске">⚠️ Не найден</span>')
        return "—"
    file_exists_badge.short_description = "Статус файла"
    
    def preview_large(self, obj):
        """Большое превью на странице редактирования."""
        if obj.url and obj.file_exists():
            return format_html(
                '''
                <div class="image-preview-large">
                    <img src="{}" id="image-preview" />
                    <div class="preview-hint">Превью изображения</div>
                </div>
                ''', 
                obj.url
            )
        elif obj.url:
            # Файл в БД есть, но на диске отсутствует
            return format_html(
                '''
                <div class="no-image-large">
                    <div style="color: red; margin-bottom: 10px;">⚠️ Файл не найден на диске</div>
                    <div>URL: {}</div>
                    <div style="margin-top: 10px; font-size: 14px;">
                        Рекомендуется загрузить изображение заново или удалить запись.
                    </div>
                </div>
                ''', 
                obj.url
            )
        return format_html('<div class="no-image-large">Изображение не загружено</div>')
    preview_large.short_description = "Предпросмотр"
    
    def filename_display(self, obj):
        """Отображение имени файла."""
        return obj.filename or "—"
    filename_display.short_description = "Имя файла"
    
    def recommended_usage_display(self, obj):
        """Отображение рекомендуемого использования."""
        return obj.recommended_usage
    recommended_usage_display.short_description = "Рекомендуемое использование"
    
    def file_exists_status(self, obj):
        """Статус файла на странице редактирования."""
        if obj.file_exists():
            return format_html('<span style="color: green; font-weight: bold;">✓ Файл найден на диске</span>')
        elif obj.url:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ Файл НЕ НАЙДЕН на диске</span>')
        return "Файл не загружен"
    file_exists_status.short_description = "Статус файла"
    
    actions = ['make_active', 'make_inactive', 'recalculate_dimensions']
    
    def recalculate_dimensions(self, request, queryset):
        """Пересчитать размеры выбранных изображений."""
        updated = 0
        for image in queryset:
            if image.image:
                image._calculate_and_update_dimensions()
                updated += 1
        
        self.message_user(
            request,
            f'Размеры пересчитаны для {updated} изображений',
            messages.SUCCESS
        )
    recalculate_dimensions.short_description = "📐 Пересчитать размеры"


class FileForm(forms.ModelForm):
    """Форма для модели File."""
    class Meta:
        model = File
        fields = '__all__'
    
    def clean_file(self):
        """Запрещает загрузку файлов с расширениями изображений."""
        file = self.cleaned_data.get('file')
        
        if file:
            file_name = file.name.lower()
            image_extensions = getattr(settings, 'IMAGE_EXTENSIONS', 
                                      ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'])
            
            if any(file_name.endswith(ext) for ext in image_extensions):
                raise ValidationError(
                    'Загрузка изображений запрещена. Используйте раздел "Изображения".'
                )
        
        return file


@admin.register(File)
class FileAdmin(ContentManagerAccessMixin, BaseAdminMixin, admin.ModelAdmin):
    """Админка для файлов."""
    form = FileForm
    
    list_display = (
        'edit_link',
        'file_icon', 
        'name_display',
        'file_type_display', 
        'size_display',
        'file_exists_badge',
        'is_active_boolean',
        'created_at_formatted'
    )
    
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'file')
    readonly_fields = (
        'created_at', 
        'updated_at', 
        'size_display',
        'filename_display',
        'extension_display',
        'file_exists_status'
    )
    list_per_page = 25
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'file')
        }),
        ('Статус', {
            'fields': ('is_active', 'file_exists_status')
        }),
        ('Техническая информация', {
            'fields': ('filename_display', 'extension_display', 'size_display'),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_icon(self, obj):
        """Иконка файла в зависимости от типа."""
        if obj.extension:
            ext = obj.extension.lower()
            icons = {
                'pdf': '📕',
                'doc': '📝', 'docx': '📝',
                'xls': '📊', 'xlsx': '📊',
                'ppt': '📽️', 'pptx': '📽️',
                'zip': '📦', 'rar': '📦',
                'txt': '📃',
            }
            return format_html('<span class="file-icon">{}</span>', icons.get(ext, '📄'))
        return "📄"
    file_icon.short_description = ""
    
    def name_display(self, obj):
        """Название файла."""
        if obj.name:
            display_text = obj.name[:60] + '...' if len(obj.name) > 60 else obj.name
            return format_html(
                '<span title="{}">{}</span>',
                obj.name,
                display_text
            )
        return "—"
    name_display.short_description = "Название"
    name_display.admin_order_field = 'name'
    
    def file_type_display(self, obj):
        """Тип файла."""
        return obj.file_type
    file_type_display.short_description = "Тип"
    
    def size_display(self, obj):
        """Размер файла."""
        return obj.size_display
    size_display.short_description = "Размер"
    
    def file_exists_badge(self, obj):
        """Бейдж статуса файла."""
        if obj.file_exists():
            return format_html('<span style="color: green;">✓ Файл найден</span>')
        elif obj.url:
            return format_html('<span style="color: red;" title="Файл отсутствует на диске">⚠️ Не найден</span>')
        return "—"
    file_exists_badge.short_description = "Статус файла"
    
    def filename_display(self, obj):
        """Имя файла."""
        return obj.filename or "—"
    filename_display.short_description = "Имя файла"
    
    def extension_display(self, obj):
        """Расширение файла."""
        return obj.extension or "—"
    extension_display.short_description = "Расширение"
    
    def file_exists_status(self, obj):
        """Статус файла на странице редактирования."""
        if obj.file_exists():
            return format_html('<span style="color: green; font-weight: bold;">✓ Файл найден на диске</span>')
        elif obj.url:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ Файл НЕ НАЙДЕН на диске</span>')
        return "Файл не загружен"
    file_exists_status.short_description = "Статус файла"
    
    actions = ['make_active', 'make_inactive']