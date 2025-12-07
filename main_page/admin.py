from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from solo.admin import SingletonModelAdmin
from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin
from core.mixins import ContentManagerAccessMixin, InlineAccessMixin
from .models import (
    HeroBlock, AdvantageBlock, AboutBlock, AnalyticsBlock, 
    PartnersBlock, ContactsBlock, Advantage, Partner
)


# ==================== ФОРМЫ ====================

class HeroBlockForm(forms.ModelForm):
    """
    Форма для приветственного блока.
    """
    class Meta:
        model = HeroBlock
        fields = '__all__'
        widgets = {
            'subtitle': forms.Textarea(attrs={'rows': 2}),
            'news_count': forms.NumberInput(attrs={
                'min': 1, 
                'max': 20, 
                'step': 1,
                'class': 'vIntegerField'
            }),
        }
    
    def clean(self):
        """
        Валидация формы.
        """
        cleaned_data = super().clean()
        
        show_news_carousel = cleaned_data.get('show_news_carousel')
        news_count = cleaned_data.get('news_count')
        
        # Если карусель новостей отключена, сбрасываем количество
        if not show_news_carousel and news_count != 5:
            self.add_error('news_count', 
                'При отключенной карусели новостей количество автоматически сбрасывается на 5')
            cleaned_data['news_count'] = 5
        
        return cleaned_data


class AdvantageForm(forms.ModelForm):
    """
    Форма для преимущества.
    """
    class Meta:
        model = Advantage
        fields = '__all__'
        widgets = {
            'order': forms.HiddenInput(),
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class PartnerForm(forms.ModelForm):
    """
    Форма для партнера.
    """
    class Meta:
        model = Partner
        fields = '__all__'
        widgets = {
            'order': forms.HiddenInput(),
        }


# ==================== INLINE ФОРМЫ ====================

class AdvantageInline(InlineAccessMixin, SortableInlineAdminMixin, admin.TabularInline):
    """
    Inline для преимуществ с drag&drop сортировкой.
    """
    model = Advantage
    form = AdvantageForm
    extra = 0
    min_num = 1
    fields = [
        'order_display', 
        'icon', 
        'icon_preview_large', 
        'title', 
        'description', 
        'is_active'
    ]
    readonly_fields = ('order_display', 'icon_preview_large')
    sortable_field_name = 'order'
    
    def order_display(self, obj):
        """
        Отображение порядка.
        """
        if obj and obj.pk:
            return obj.order
        return '—'
    order_display.short_description = 'Порядок'
    
    def icon_preview_large(self, obj):
        """
        Превью иконки преимущества.
        """
        if obj.icon_url:
            return format_html(
                '''
                <div style="position: relative; max-width: 100px;">
                    <a href="{}" target="_blank" style="display: block;">
                        <img src="{}" style="
                            max-height: 80px; 
                            max-width: 100%; 
                            cursor: pointer; 
                            border: 1px solid #555; 
                            border-radius: 4px; 
                            transition: 0.3s;
                            object-fit: contain;
                        " 
                        onmouseover="this.style.transform='scale(1.02)'; 
                                     this.style.boxShadow='0 4px 8px rgba(0,0,0,0.2)';" 
                        onmouseout="this.style.transform='scale(1)'; 
                                    this.style.boxShadow='none';"
                        title="Нажмите для просмотра в полный размер"
                        />
                    </a>
                    <div style="text-align: center; margin-top: 5px; font-size: 11px; color: #666;">
                        Иконка
                    </div>
                </div>
                ''', 
                obj.icon_url,
                obj.icon_url
            )
        return format_html(
            '''
            <div style="padding: 15px; background: #f8f9fa; border: 1px dashed #555; 
                 text-align: center; border-radius: 4px; margin: 5px 0;">
                <span style="color: #999; font-size: 11px;">
                    Иконка не выбрана
                </span>
            </div>
            '''
        )
    icon_preview_large.short_description = "Превью иконки"


class PartnerInline(InlineAccessMixin, SortableInlineAdminMixin, admin.TabularInline):
    """
    Inline для партнеров с drag&drop сортировкой.
    """
    model = Partner
    form = PartnerForm
    extra = 0
    min_num = 1
    fields = [
        'order_display', 
        'logo', 
        'logo_preview_large', 
        'name', 
        'website', 
        'website_preview',
        'is_active'
    ]
    readonly_fields = ('order_display', 'logo_preview_large', 'website_preview')
    sortable_field_name = 'order'
    
    def order_display(self, obj):
        """
        Отображение порядка.
        """
        if obj and obj.pk:
            return obj.order
        return '—'
    order_display.short_description = 'Порядок'
    
    def logo_preview_large(self, obj):
        """
        Превью логотипа партнера.
        """
        if obj.logo_url:
            return format_html(
                '''
                <div style="position: relative; max-width: 120px;">
                    <a href="{}" target="_blank" style="display: block;">
                        <img src="{}" style="
                            max-height: 60px; 
                            max-width: 100%; 
                            cursor: pointer; 
                            border: 1px solid #555; 
                            border-radius: 4px; 
                            transition: 0.3s;
                            object-fit: contain;
                            background: white;
                            padding: 5px;
                        " 
                        onmouseover="this.style.transform='scale(1.02)'; 
                                     this.style.boxShadow='0 4px 8px rgba(0,0,0,0.2)';" 
                        onmouseout="this.style.transform='scale(1)'; 
                                    this.style.boxShadow='none';"
                        title="Нажмите для просмотра в полный размер"
                        />
                    </a>
                    <div style="text-align: center; margin-top: 5px; font-size: 11px; color: #666;">
                        Логотип
                    </div>
                </div>
                ''', 
                obj.logo_url,
                obj.logo_url
            )
        return format_html(
            '''
            <div style="padding: 15px; background: #f8f9fa; border: 1px dashed #555; 
                 text-align: center; border-radius: 4px; margin: 5px 0;">
                <span style="color: #999; font-size: 11px;">
                    Логотип не выбран
                </span>
            </div>
            '''
        )
    logo_preview_large.short_description = "Превью логотипа"
    
    def website_preview(self, obj):
        """
        Предпросмотр сайта партнера.
        """
        if obj.website:
            return format_html(
                '<a href="{}" target="_blank" style="font-size: 12px;">🔗 Открыть сайт</a>',
                obj.website
            )
        return "—"
    website_preview.short_description = "Сайт"


# ==================== SINGLETON АДМИНКИ ====================

@admin.register(HeroBlock)
class HeroBlockAdmin(ContentManagerAccessMixin, SingletonModelAdmin):
    """
    Админка для приветственного блока.
    """
    form = HeroBlockForm
    
    fieldsets = (
        (_('Основные настройки'), {
            'fields': ('background_image', 'background_preview_large')
        }),
        (_('Текстовое содержание'), {
            'fields': ('title', 'subtitle', 'cta_button_text')
        }),
        (_('Настройки новостей'), {
            'fields': ('show_news_carousel', 'news_count'),
            'description': _('Карусель будет показывать последние N активных новостей')
        }),
        (_('Статус'), {
            'fields': ('is_active',),
        }),
    )
    
    readonly_fields = ['background_preview_large']
    
    def background_preview_large(self, obj):
        """
        Большое превью фонового изображения.
        """
        if obj.background_image and obj.background_image.image:
            return format_html(
                '''
                <div style="position: relative; max-width: 600px; margin: 10px 0;">
                    <a href="{}" target="_blank" style="display: block; text-decoration: none;">
                        <img src="{}" style="
                            max-height: 300px; 
                            max-width: 100%; 
                            cursor: pointer; 
                            border: 1px solid #555; 
                            border-radius: 8px; 
                            transition: all 0.3s ease;
                            object-fit: cover;
                        " 
                        onmouseover="this.style.transform='scale(1.01)'; 
                                     this.style.boxShadow='0 8px 16px rgba(0,0,0,0.2)';" 
                        onmouseout="this.style.transform='scale(1)'; 
                                    this.style.boxShadow='none';"
                        title="Нажмите для просмотра в полный размер"
                        />
                    </a>
                    <div style="text-align: center; margin-top: 8px; font-size: 12px; color: #666;">
                        Фоновое изображение для приветственного блока
                    </div>
                </div>
                ''',
                obj.background_image.image.url,
                obj.background_image.image.url
            )
        return format_html(
            '''
            <div style="padding: 30px; background: #f8f9fa; border: 1px dashed #555; 
                 text-align: center; border-radius: 8px; margin: 10px 0;">
                <span style="color: #999; font-size: 14px;">
                    Фоновое изображение не выбрано
                </span>
            </div>
            '''
        )
    background_preview_large.short_description = _('Предпросмотр фона')


@admin.register(AboutBlock)
class AboutBlockAdmin(ContentManagerAccessMixin, SingletonModelAdmin):
    """
    Админка для блока "О компании".
    """
    fieldsets = (
        (_('Текстовое содержание'), {
            'fields': ('title', 'subtitle', 'content')
        }),
        (_('Статус'), {
            'fields': ('is_active',),
        }),
    )


@admin.register(AdvantageBlock)
class AdvantageBlockAdmin(ContentManagerAccessMixin, SortableAdminBase, SingletonModelAdmin):
    """
    Админка для блока преимуществ.
    """
    fieldsets = (
        (_('Текстовое содержание'), {
            'fields': ('title', 'subtitle', 'content')
        }),
        (_('Статус'), {
            'fields': ('is_active',),
        }),
    )
    
    inlines = [AdvantageInline]
    
    def get_queryset(self, request):
        """
        Аннотируем количество преимуществ.
        """
        from django.db.models import Count
        return super().get_queryset(request).annotate(
            advantages_count=Count('advantages')
        )


@admin.register(AnalyticsBlock)
class AnalyticsBlockAdmin(ContentManagerAccessMixin, SingletonModelAdmin):
    """
    Админка для блока бизнес-аналитики.
    """
    
    fieldsets = (
        (_('Текстовое содержание'), {
            'fields': ('title', 'subtitle', 'content')
        }),
        (_('Диаграммы'), {
            'fields': ('diagram_1', 'diagram_2'),
            'description': _('Выберите диаграммы из раздела "Бизнес-аналитика"')
        }),
        (_('Статус'), {
            'fields': ('is_active',),
        }),
    )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Фильтруем только активные диаграммы.
        """
        if db_field.name in ['diagram_1', 'diagram_2']:
            from business_analytics.models import Diagram
            kwargs["queryset"] = Diagram.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def has_diagrams_display(self, obj):
        """
        Отображение информации о диаграммах.
        """
        if obj.has_diagrams:
            return format_html(
                '<span style="color: #32CD32; font-weight: bold;">✓ Есть диаграммы</span>'
            )
        return format_html(
            '<span style="color: #DC143C;">✗ Нет диаграмм</span>'
        )
    has_diagrams_display.short_description = "Диаграммы"


@admin.register(PartnersBlock)
class PartnersBlockAdmin(ContentManagerAccessMixin, SortableAdminBase, SingletonModelAdmin):
    """
    Админка для блока партнеров.
    """
    fieldsets = (
        (_('Текстовое содержание'), {
            'fields': ('title', 'subtitle', 'content')
        }),
        (_('Статус'), {
            'fields': ('is_active',),
        }),
    )
    
    inlines = [PartnerInline]
    
    def get_queryset(self, request):
        """
        Аннотируем количество партнеров.
        """
        from django.db.models import Count
        return super().get_queryset(request).annotate(
            partners_count=Count('partners')
        )


@admin.register(ContactsBlock)
class ContactsBlockAdmin(ContentManagerAccessMixin, SingletonModelAdmin):
    """
    Админка для блока контактов.
    """
    fieldsets = (
        (_('Текстовое содержание'), {
            'fields': ('title', 'subtitle', 'content', 'cta_button_text')
        }),
        (_('Статус'), {
            'fields': ('is_active',),
        }),
    )