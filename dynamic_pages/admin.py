from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from solo.admin import SingletonModelAdmin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from core.mixins import ContentManagerAccessMixin, InlineAccessMixin
from .models import (
    AboutPage, ServicesPage, DocumentsPage,
    AboutSection, ServiceSection, DocumentSection,
    SectionImage, SectionFile
)


# ==================== СИНГЛТОН-СТРАНИЦЫ ====================

@admin.register(AboutPage)
class AboutPageAdmin(ContentManagerAccessMixin, SingletonModelAdmin):
    """
    Админка для страницы 'О компании'.
    """
    fields = ('title', 'meta_title', 'meta_description', 'updated_at')
    readonly_fields = ('updated_at',)
    
    def has_add_permission(self, request):
        """
        Синглтон-модель нельзя добавлять.
        """
        return False


@admin.register(ServicesPage)
class ServicesPageAdmin(ContentManagerAccessMixin, SingletonModelAdmin):
    """
    Админка для страницы 'Услуги'.
    """
    fields = ('title', 'meta_title', 'meta_description', 'updated_at')
    readonly_fields = ('updated_at',)
    
    def has_add_permission(self, request):
        """
        Синглтон-модель нельзя добавлять.
        """
        return False


@admin.register(DocumentsPage)
class DocumentsPageAdmin(ContentManagerAccessMixin, SingletonModelAdmin):
    """
    Админка для страницы 'Документы'.
    """
    fields = ('title', 'meta_title', 'meta_description', 'updated_at')
    readonly_fields = ('updated_at',)
    
    def has_add_permission(self, request):
        """
        Синглтон-модель нельзя добавлять.
        """
        return False


# ==================== INLINE ДЛЯ МЕДИА С DRAG-AND-DROP ====================

class SectionImageInline(InlineAccessMixin, SortableInlineAdminMixin, admin.TabularInline):
    """
    Inline для изображений секций с drag-and-drop сортировкой.
    """
    model = SectionImage
    extra = 0
    min_num = 0
    fields = ('order_display', 'image', 'image_preview', 'actions')
    readonly_fields = ('order_display', 'image_preview', 'actions')
    ordering = ['order']
    
    def order_display(self, obj):
        """
        Отображение порядка с drag-handle.
        """
        if obj and obj.pk:
            return format_html(
                '''
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="drag-handle" style="cursor: move; font-size: 16px; color: #ccc; user-select: none;">⋮⋮</span>
                    <span>{}</span>
                </div>
                ''',
                obj.order
            )
        return "—"
    order_display.short_description = "Порядок"
    
    def image_preview(self, obj):
        """
        Превью изображения.
        """
        if obj.image_url:
            return format_html(
                '''
                <div style="position: relative; max-width: 200px; margin: 5px 0;">
                    <a href="{}" target="_blank" style="display: block;">
                        <img src="{}" style="
                            max-height: 100px; 
                            max-width: 100%; 
                            cursor: pointer; 
                            border: 1px solid #555; 
                            border-radius: 4px; 
                            transition: 0.3s;
                            object-fit: cover;
                        " 
                        onmouseover="this.style.transform='scale(1.02)'; 
                                     this.style.boxShadow='0 4px 8px rgba(0,0,0,0.2)';" 
                        onmouseout="this.style.transform='scale(1)'; 
                                    this.style.boxShadow='none';"
                        title="Нажмите для просмотра в полный размер"
                        />
                    </a>
                </div>
                ''', 
                obj.image_url,
                obj.image_url
            )
        return format_html(
            '''
            <div style="padding: 10px; background: #f8f9fa; border: 1px dashed #555; 
                 text-align: center; border-radius: 4px; margin: 5px 0;">
                <span style="color: #999; font-size: 12px;">
                    Изображение не выбрано
                </span>
            </div>
            '''
        )
    image_preview.short_description = "Превью"
    
    def actions(self, obj):
        """
        Кнопки действий для inline.
        """
        if obj.image and obj.image.id:
            url = reverse('admin:core_image_change', args=[obj.image.id])
            return format_html(
                '''
                <a href="{}" target="_blank" style="
                    padding: 3px 8px;
                    background: #417690;
                    color: white;
                    text-decoration: none;
                    border-radius: 3px;
                    font-size: 11px;
                    border: none;
                    cursor: pointer;
                " title="Редактировать изображение">✏️</a>
                ''',
                url
            )
        return "—"
    actions.short_description = "Действия"


class SectionFileInline(InlineAccessMixin, SortableInlineAdminMixin, admin.TabularInline):
    """
    Inline для файлов секций с drag-and-drop сортировкой.
    """
    model = SectionFile
    extra = 0
    min_num = 0
    fields = ('order_display', 'file', 'file_info', 'download_link', 'actions')
    readonly_fields = ('order_display', 'file_info', 'download_link', 'actions')
    ordering = ['order']
    
    def order_display(self, obj):
        """
        Отображение порядка с drag-handle.
        """
        if obj and obj.pk:
            return format_html(
                '''
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="drag-handle" style="cursor: move; font-size: 16px; color: #ccc; user-select: none;">⋮⋮</span>
                    <span>{}</span>
                </div>
                ''',
                obj.order
            )
        return "—"
    order_display.short_description = "Порядок"
    
    def file_info(self, obj):
        """
        Информация о файле.
        """
        if obj.file:
            info_parts = []
            
            # Имя файла
            if obj.file_name:
                info_parts.append(f"<strong>{obj.file_name}</strong>")
            
            # Размер файла
            if obj.file_size_display != "—":
                info_parts.append(f"<br>📏 {obj.file_size_display}")
            
            # Расширение файла
            if obj.file_extension:
                info_parts.append(f"<br>📄 {obj.file_extension}")
            
            # Описание
            if obj.file.description:
                info_parts.append(f"<br>📝 {obj.file.description[:50]}..." 
                                if len(obj.file.description) > 50 
                                else f"<br>📝 {obj.file.description}")
            
            if info_parts:
                return format_html(''.join(info_parts))
        
        return "—"
    file_info.short_description = "Информация"
    
    def download_link(self, obj):
        """
        Ссылка для скачивания файла.
        """
        if obj.file_url:
            return format_html(
                '''
                <a href="{}" target="_blank" download style="
                    padding: 3px 8px;
                    background: #5cb85c;
                    color: white;
                    text-decoration: none;
                    border-radius: 3px;
                    font-size: 11px;
                    border: none;
                    cursor: pointer;
                    display: inline-block;
                    margin-top: 5px;
                " title="Скачать файл">📥 Скачать</a>
                ''',
                obj.file_url
            )
        return "—"
    download_link.short_description = "Скачать"
    
    def actions(self, obj):
        """
        Кнопки действий для inline.
        """
        if obj.file and obj.file.id:
            file_url = reverse('admin:core_file_change', args=[obj.file.id])
            return format_html(
                '''
                <a href="{}" target="_blank" style="
                    padding: 3px 8px;
                    background: #f0ad4e;
                    color: white;
                    text-decoration: none;
                    border-radius: 3px;
                    font-size: 11px;
                    border: none;
                    cursor: pointer;
                " title="Редактировать файл">✏️</a>
                ''',
                file_url
            )
        return "—"
    actions.short_description = "Действия"


# ==================== БАЗОВЫЙ КЛАСС ДЛЯ СЕКЦИЙ ====================

class BaseSectionAdmin(ContentManagerAccessMixin, SortableAdminMixin, admin.ModelAdmin):
    """
    Базовый класс админки для секций.
    """
    
    list_display = (
        'menu_title_display', 
        'title_display', 
        'layout_display', 
        'order_display', 
        'is_active_display'
    )
    list_editable = ()
    readonly_fields = ('created_at', 'updated_at')
    ordering = ['order']
    list_filter = ('layout', 'is_active', 'created_at')
    search_fields = ('title', 'menu_title', 'content', 'subtitle')
    list_per_page = 25
    
    inlines = [SectionImageInline, SectionFileInline]
    
    # Добавляем поля для SortableAdminMixin
    fields = ['about_page', 'services_page', 'documents_page', 'menu_title', 'title', 'subtitle', 'content', 
              'layout', 'order', 'is_active', 'created_at', 'updated_at']
    
    def get_fields(self, request, obj=None):
        """
        Переопределяем метод get_fields для совместимости с SortableAdminMixin.
        """
        # Создаем базовый список полей
        fields = list(super().get_fields(request, obj))
        
        # Убираем лишние поля в зависимости от типа секции
        if self.model == AboutSection:
            fields = [f for f in fields if f not in ['services_page', 'documents_page']]
        elif self.model == ServiceSection:
            fields = [f for f in fields if f not in ['about_page', 'documents_page']]
        elif self.model == DocumentSection:
            fields = [f for f in fields if f not in ['about_page', 'services_page']]
        
        return fields
    
    def get_readonly_fields(self, request, obj=None):
        """
        Получаем поля только для чтения.
        """
        readonly_fields = list(super().get_readonly_fields(request, obj))
        readonly_fields.extend(['created_at', 'updated_at'])
        return readonly_fields
    
    def menu_title_display(self, obj):
        """
        Отображение названия в меню.
        """
        if obj.menu_title:
            change_url = reverse(f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change', args=[obj.id])
            return format_html(
                '<a href="{}" style="font-weight: bold; color: #417690;">{}</a>',
                change_url,
                obj.menu_title
            )
        return "—"
    menu_title_display.short_description = "Название в меню"
    menu_title_display.admin_order_field = 'menu_title'
    
    def title_display(self, obj):
        """
        Отображение заголовка.
        """
        if obj.title:
            change_url = reverse(f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change', args=[obj.id])
            display_text = obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
            return format_html(
                '<a href="{}" style="color: #666;">{}</a>',
                change_url,
                display_text
            )
        return "—"
    title_display.short_description = "Заголовок"
    title_display.admin_order_field = 'title'
    
    def layout_display(self, obj):
        """
        Отображение макета.
        """
        layout_map = {
            'layout_1': 'Текст → Img → Файлы',
            'layout_2': 'Img → Текст → Файлы',
            'layout_3': 'Img | Текст → Файлы',
            'layout_4': 'Текст | Img → Файлы',
        }
        return layout_map.get(obj.layout, obj.layout)
    layout_display.short_description = "Макет"
    layout_display.admin_order_field = 'layout'
    
    def order_display(self, obj):
        """
        Отображение порядка.
        """
        return obj.order
    order_display.short_description = "Порядок"
    order_display.admin_order_field = 'order'
    
    def is_active_display(self, obj):
        """
        Отображение активности.
        """
        if obj.is_active:
            return format_html(
                '<span style="color: #32CD32; font-weight: bold;">✓</span>'
            )
        return format_html(
            '<span style="color: #DC143C;">✗</span>'
        )
    is_active_display.short_description = "Активно"
    is_active_display.admin_order_field = 'is_active'


# ==================== АДМИНКИ ДЛЯ СЕКЦИЙ ====================

@admin.register(AboutSection)
class AboutSectionAdmin(BaseSectionAdmin):
    """
    Админка для секций 'О компании'.
    """
    
    def get_fieldsets(self, request, obj=None):
        """
        Определяем fieldsets для AboutSection.
        """
        return (
            ('Основная информация', {
                'fields': ('about_page', 'menu_title', 'title', 'subtitle', 'content', 'layout')
            }),
            ('Настройки', {
                'fields': ('order', 'is_active')
            }),
            ('Системная информация', {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',)
            }),
        )
    
    def get_queryset(self, request):
        """
        Оптимизированный queryset.
        """
        qs = super().get_queryset(request)
        about_page = AboutPage.get_solo()
        return qs.filter(about_page=about_page)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Устанавливаем начальное значение для about_page.
        """
        if db_field.name == "about_page":
            about_page = AboutPage.get_solo()
            kwargs["initial"] = about_page
            kwargs["queryset"] = AboutPage.objects.filter(id=about_page.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ServiceSection)
class ServiceSectionAdmin(BaseSectionAdmin):
    """
    Админка для секций 'Услуги'.
    """
    
    def get_fieldsets(self, request, obj=None):
        """
        Определяем fieldsets для ServiceSection.
        """
        return (
            ('Основная информация', {
                'fields': ('services_page', 'menu_title', 'title', 'subtitle', 'content', 'layout')
            }),
            ('Настройки', {
                'fields': ('order', 'is_active')
            }),
            ('Системная информация', {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',)
            }),
        )
    
    def get_queryset(self, request):
        """
        Оптимизированный queryset.
        """
        qs = super().get_queryset(request)
        services_page = ServicesPage.get_solo()
        return qs.filter(services_page=services_page)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Устанавливаем начальное значение для services_page.
        """
        if db_field.name == "services_page":
            services_page = ServicesPage.get_solo()
            kwargs["initial"] = services_page
            kwargs["queryset"] = ServicesPage.objects.filter(id=services_page.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(DocumentSection)
class DocumentSectionAdmin(BaseSectionAdmin):
    """
    Админка для секций 'Документы'.
    """
    
    def get_fieldsets(self, request, obj=None):
        """
        Определяем fieldsets для DocumentSection.
        """
        return (
            ('Основная информация', {
                'fields': ('documents_page', 'menu_title', 'title', 'subtitle', 'content', 'layout')
            }),
            ('Настройки', {
                'fields': ('order', 'is_active')
            }),
            ('Системная информация', {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',)
            }),
        )
    
    def get_queryset(self, request):
        """
        Оптимизированный queryset.
        """
        qs = super().get_queryset(request)
        documents_page = DocumentsPage.get_solo()
        return qs.filter(documents_page=documents_page)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Устанавливаем начальное значение для documents_page.
        """
        if db_field.name == "documents_page":
            documents_page = DocumentsPage.get_solo()
            kwargs["initial"] = documents_page
            kwargs["queryset"] = DocumentsPage.objects.filter(id=documents_page.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)