from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import News

def news_list(request):
    """Список всех опубликованных новостей"""
    news_list = News.objects.filter(
        is_active=True,
        publish_date__lte=timezone.now()
    ).order_by('-publish_date')
    
    context = {
        'news_list': news_list,
    }
    return render(request, 'news/news_list.html', context)

def news_detail(request, slug):
    """Детальная страница новости"""
    news = get_object_or_404(
        News, 
        slug=slug,
        is_active=True,
        publish_date__lte=timezone.now()
    )
    
    # Дополнительные изображения и файлы
    additional_images = news.news_images.select_related('image').all()
    attached_files = news.news_files.select_related('file').all()
    
    context = {
        'news': news,
        'additional_images': additional_images,
        'attached_files': attached_files,
    }
    return render(request, 'news/news_detail.html', context)