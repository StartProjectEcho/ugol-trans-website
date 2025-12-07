from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.conf import settings
from core.mixins import ContentManagerAccessMixin
from adminsortable2.admin import SortableAdminMixin
from .models import Phone, Email, Address, SocialMedia


# ==================== ФОРМЫ ====================

class PhoneAdminForm(forms.ModelForm):
    """
    Форма для телефона.
    """
    class Meta:
        model = Phone
        fields = '__all__'
        widgets = {
            'number': forms.TextInput(attrs={
                'placeholder': '+7 999 123-45-67',
                'class': 'vTextField'
            }),
            'description': forms.TextInput(attrs={
                'placeholder': 'Главный офис, Отдел продаж',
                'class': 'vTextField'
            }),
        }


class EmailAdminForm(forms.ModelForm):
    """
    Форма для email.
    """
    class Meta:
        model = Email
        fields = '__all__'
        widgets = {
            'address': forms.EmailInput(attrs={
                'placeholder': 'info@ugol-trans.ru',
                'class': 'vTextField'
            }),
        }


class AddressAdminForm(forms.ModelForm):
    """
    Форма для адреса.
    """
    class Meta:
        model = Address
        fields = '__all__'
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'г. Москва, ул. Примерная, д. 1, офис 101'
            }),
            'map_link': forms.URLInput(attrs={
                'placeholder': 'https://yandex.ru/maps/?text=...'
            }),
        }


class SocialMediaAdminForm(forms.ModelForm):
    """
    Форма для социальной сети с автопредпросмотром иконки.
    """
    class Meta:
        model = SocialMedia
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'ВКонтакте, Telegram, YouTube'
            }),
            'url': forms.URLInput(attrs={
                'placeholder': 'https://vk.com/ugol_trans'
            }),
        }


# ==================== КЛАССЫ АДМИНКИ ====================

@admin.register(Phone)
class PhoneAdmin(ContentManagerAccessMixin, SortableAdminMixin, admin.ModelAdmin):
    """
    Админка для телефонов.
    """
    form = PhoneAdminForm
    
    # ✏️ ПЕРВЫЙ СТОЛБЕЦ - ИЗМЕНИТЬ
    list_display = (
        'edit_link',
        'number_display',
        'description_display',
        'order_display',
        'is_active_display',
        'created_at_formatted',
    )
    
    list_filter = ('is_active', 'created_at')
    search_fields = ('number', 'description')
    list_per_page = 25
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('number', 'description', 'order', 'is_active')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    # ==================== КОЛОНКИ ====================
    def edit_link(self, obj):
        """Ссылка на редактирование в виде текста с карандашиком."""
        url = reverse('admin:contacts_phone_change', args=[obj.id])
        return format_html(
            '<a href="{}" style="text-decoration: none; color: #447e9b;" title="Редактировать">'
            '<span style="font-size: 14px;">✏️</span> Изменить'
            '</a>',
            url
        )
    edit_link.short_description = ''
    
    def number_display(self, obj):
        """Номер телефона БЕЗ ссылки."""
        return obj.formatted_number
    number_display.short_description = 'Номер телефона'
    number_display.admin_order_field = 'number'
    
    def description_display(self, obj):
        """Описание БЕЗ ссылки."""
        return obj.description or "—"
    description_display.short_description = 'Описание'
    
    def order_display(self, obj):
        """Порядок."""
        return obj.order
    order_display.short_description = 'Порядок'
    order_display.admin_order_field = 'order'
    
    def is_active_display(self, obj):
        """Активность."""
        if obj.is_active:
            return "✅"
        else:
            return "❌"
    is_active_display.short_description = 'Активно'
    is_active_display.admin_order_field = 'is_active'
    
    def created_at_formatted(self, obj):
        """Дата создания."""
        return obj.created_at.strftime('%d.%m.%Y')
    created_at_formatted.short_description = 'Создан'
    created_at_formatted.admin_order_field = 'created_at'
    
    # ==================== ДЕЙСТВИЯ ====================
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        """Активировать выбранные телефоны."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, 
            f'Активировано телефонов: {updated}', 
            messages.SUCCESS
        )
    make_active.short_description = "✅ Активировать"
    
    def make_inactive(self, request, queryset):
        """Деактивировать выбранные телефоны."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, 
            f'Деактивировано телефонов: {updated}', 
            messages.SUCCESS
        )
    make_inactive.short_description = "❌ Деактивировать"


@admin.register(Email)
class EmailAdmin(ContentManagerAccessMixin, SortableAdminMixin, admin.ModelAdmin):
    """
    Админка для email.
    """
    form = EmailAdminForm
    
    # ✏️ ПЕРВЫЙ СТОЛБЕЦ - ИЗМЕНИТЬ
    list_display = (
        'edit_link',
        'address_display',
        'description_display',
        'domain_display',
        'order_display',
        'is_active_display',
    )
    
    list_filter = ('is_active',)
    search_fields = ('address', 'description')
    list_per_page = 25
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('address', 'description', 'order', 'is_active')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    # ==================== КОЛОНКИ ====================
    def edit_link(self, obj):
        """Ссылка на редактирование в виде текста с карандашиком."""
        url = reverse('admin:contacts_email_change', args=[obj.id])
        return format_html(
            '<a href="{}" style="text-decoration: none; color: #447e9b;" title="Редактировать">'
            '<span style="font-size: 14px;">✏️</span> Изменить'
            '</a>',
            url
        )
    edit_link.short_description = ''
    
    def address_display(self, obj):
        """Email БЕЗ ссылки."""
        return obj.address
    address_display.short_description = 'Email'
    address_display.admin_order_field = 'address'
    
    def description_display(self, obj):
        """Описание БЕЗ ссылки."""
        return obj.description or "—"
    description_display.short_description = 'Описание'
    
    def domain_display(self, obj):
        """Домен."""
        return format_html(
            '<code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px;">{}</code>',
            obj.domain
        )
    domain_display.short_description = 'Домен'
    
    def order_display(self, obj):
        """Порядок."""
        return obj.order
    order_display.short_description = 'Порядок'
    order_display.admin_order_field = 'order'
    
    def is_active_display(self, obj):
        """Активность."""
        if obj.is_active:
            return "✅"
        else:
            return "❌"
    is_active_display.short_description = 'Активно'
    is_active_display.admin_order_field = 'is_active'
    
    # ==================== ДЕЙСТВИЯ ====================
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        """Активировать выбранные email."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, 
            f'Активировано email: {updated}', 
            messages.SUCCESS
        )
    make_active.short_description = "✅ Активировать"
    
    def make_inactive(self, request, queryset):
        """Деактивировать выбранные email."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, 
            f'Деактивировано email: {updated}', 
            messages.SUCCESS
        )
    make_inactive.short_description = "❌ Деактивировать"


@admin.register(Address)
class AddressAdmin(ContentManagerAccessMixin, SortableAdminMixin, admin.ModelAdmin):
    """
    Админка для адресов.
    """
    form = AddressAdminForm
    
    # ✏️ ПЕРВЫЙ СТОЛБЕЦ - ИЗМЕНИТЬ
    list_display = (
        'edit_link',
        'short_address_display',
        'description_display',
        'map_type_display',
        'order_display',
        'is_active_display',
    )
    
    list_filter = ('is_active',)
    search_fields = ('text', 'description')
    list_per_page = 25
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('text', 'description', 'map_link', 'order', 'is_active')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    # ==================== КОЛОНКИ ====================
    def edit_link(self, obj):
        """Ссылка на редактирование в виде текста с карандашиком."""
        url = reverse('admin:contacts_address_change', args=[obj.id])
        return format_html(
            '<a href="{}" style="text-decoration: none; color: #447e9b;" title="Редактировать">'
            '<span style="font-size: 14px;">✏️</span> Изменить'
            '</a>',
            url
        )
    edit_link.short_description = ''
    
    def short_address_display(self, obj):
        """Краткий адрес БЕЗ ссылки."""
        return obj.short_address
    short_address_display.short_description = 'Адрес'
    short_address_display.admin_order_field = 'text'
    
    def description_display(self, obj):
        """Описание БЕЗ ссылки."""
        return obj.description or "—"
    description_display.short_description = 'Описание'
    
    def map_type_display(self, obj):
        """Тип карты."""
        if obj.map_link:
            if obj.is_yandex_map:
                return format_html('<span style="color: #FF0000;">🗺️ Яндекс.Карты</span>')
            elif obj.is_google_map:
                return format_html('<span style="color: #4285F4;">🗺️ Google Maps</span>')
            else:
                return format_html('<span>🗺️ Другая карта</span>')
        return "—"
    map_type_display.short_description = 'Карта'
    
    def order_display(self, obj):
        """Порядок."""
        return obj.order
    order_display.short_description = 'Порядок'
    order_display.admin_order_field = 'order'
    
    def is_active_display(self, obj):
        """Активность."""
        if obj.is_active:
            return "✅"
        else:
            return "❌"
    is_active_display.short_description = 'Активно'
    is_active_display.admin_order_field = 'is_active'
    
    # ==================== ДЕЙСТВИЯ ====================
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        """Активировать выбранные адреса."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, 
            f'Активировано адресов: {updated}', 
            messages.SUCCESS
        )
    make_active.short_description = "✅ Активировать"
    
    def make_inactive(self, request, queryset):
        """Деактивировать выбранные адреса."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, 
            f'Деактивировано адресов: {updated}', 
            messages.SUCCESS
        )
    make_inactive.short_description = "❌ Деактивировать"


@admin.register(SocialMedia)
class SocialMediaAdmin(ContentManagerAccessMixin, SortableAdminMixin, admin.ModelAdmin):
    """
    Админка для социальных сетей с автопредпросмотром иконок.
    """
    form = SocialMediaAdminForm
    
    # ✏️ ПЕРВЫЙ СТОЛБЕЦ - ИЗМЕНИТЬ
    list_display = (
        'edit_link',
        'name_display',
        'platform_icon_display',
        'url_preview',
        'order_display',
        'is_active_display',
    )
    
    list_filter = ('is_active',)
    search_fields = ('name', 'url')
    list_per_page = 25
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'icon', 'url', 'order', 'is_active')
        }),
        ('Дополнительная информация', {
            'fields': ('icon_preview_large', 'recommended_size_display'),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'icon_preview_large', 'recommended_size_display')
    
    class Media:
        css = {
            'all': ('admin/css/contacts.css',)
        }
        js = ('admin/js/image_preview.js',)
    
    # ==================== КОЛОНКИ ====================
    def edit_link(self, obj):
        """Ссылка на редактирование в виде текста с карандашиком."""
        url = reverse('admin:contacts_socialmedia_change', args=[obj.id])
        return format_html(
            '<a href="{}" style="text-decoration: none; color: #447e9b;" title="Редактировать">'
            '<span style="font-size: 14px;">✏️</span> Изменить'
            '</a>',
            url
        )
    edit_link.short_description = ''
    
    def name_display(self, obj):
        """Название БЕЗ ссылки."""
        return obj.name
    name_display.short_description = 'Название'
    name_display.admin_order_field = 'name'
    
    def platform_icon_display(self, obj):
        """Иконка платформы."""
        if obj.icon_url:
            return format_html(
                '''
                <div style="display: flex; align-items: center; gap: 8px;">
                    <img src="{}" style="
                        max-height: 24px; 
                        max-width: 24px; 
                        border-radius: 4px;
                        border: 1px solid #ddd;
                    " />
                </div>
                ''',
                obj.icon_url
            )
        else:
            return "—"
    platform_icon_display.short_description = 'Иконка'
    
    def url_preview(self, obj):
        """Предпросмотр ссылки."""
        if obj.url:
            display_url = obj.url
            if len(display_url) > 40:
                display_url = display_url[:37] + '...'
            return format_html(
                '<a href="{}" target="_blank" title="{}" style="color: #666;">🔗 {}</a>',
                obj.url,
                obj.url,
                display_url
            )
        return "—"
    url_preview.short_description = 'Ссылка'
    
    def order_display(self, obj):
        """Порядок."""
        return obj.order
    order_display.short_description = 'Порядок'
    order_display.admin_order_field = 'order'
    
    def is_active_display(self, obj):
        """Активность."""
        if obj.is_active:
            return "✅"
        else:
            return "❌"
    is_active_display.short_description = 'Активно'
    is_active_display.admin_order_field = 'is_active'
    
    # ==================== ПОЛЯ ТОЛЬКО ДЛЯ ЧТЕНИЯ ====================
    def icon_preview_large(self, obj):
        """Большое превью иконки на странице редактирования."""
        if obj.icon_url:
            return format_html(
                '''
                <div class="image-preview-large" style="max-width: 200px; margin: 10px 0;">
                    <a href="{}" target="_blank">
                        <img src="{}" style="
                            max-height: 100px; 
                            max-width: 100%; 
                            cursor: pointer; 
                            border: 1px solid #555; 
                            border-radius: 8px; 
                            transition: all 0.3s ease;
                            object-fit: contain;
                            padding: 10px;
                            background: white;
                        " 
                        onmouseover="this.style.transform='scale(1.02)'; 
                                     this.style.boxShadow='0 8px 16px rgba(0,0,0,0.2)';" 
                        onmouseout="this.style.transform='scale(1)'; 
                                    this.style.boxShadow='none';"
                        title="Нажмите для просмотра в полный размер"
                        />
                    </a>
                    <div style="text-align: center; margin-top: 5px; font-size: 12px; color: #666;">
                        Рекомендуемый размер: {}
                    </div>
                </div>
                ''', 
                obj.icon_url,
                obj.icon_url,
                obj.recommended_icon_size
            )
        return format_html(
            '''
            <div style="padding: 20px; background: #f8f9fa; border: 1px solid #555; 
                 text-align: center; border-radius: 8px; margin: 10px 0;">
                <span style="color: #999; font-size: 14px;">
                    Иконка не выбрана
                </span>
                <div style="margin-top: 10px; font-size: 12px; color: #666;">
                    Рекомендуемый размер: {}
                </div>
            </div>
            ''',
            obj.recommended_icon_size
        )
    icon_preview_large.short_description = 'Предпросмотр иконки'
    
    def recommended_size_display(self, obj):
        """Рекомендуемый размер иконки."""
        return f"{obj.recommended_icon_size} пикселей"
    recommended_size_display.short_description = 'Рекомендуемый размер'
    
    # ==================== ДЕЙСТВИЯ ====================
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        """Активировать выбранные соцсети."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, 
            f'Активировано соцсетей: {updated}', 
            messages.SUCCESS
        )
    make_active.short_description = "✅ Активировать"
    
    def make_inactive(self, request, queryset):
        """Деактивировать выбранные соцсети."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, 
            f'Деактивировано соцсетей: {updated}', 
            messages.SUCCESS
        )
    make_inactive.short_description = "❌ Деактивировать"