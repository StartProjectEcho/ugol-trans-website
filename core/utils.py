"""
Вспомогательные функции и утилиты.
"""
import os
import hashlib
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings


def generate_file_hash(file_content):
    """
    Генерирует MD5 хэш для файла.
    """
    return hashlib.md5(file_content).hexdigest()


def save_uploaded_file(file, upload_to='uploads/'):
    """
    Сохраняет загруженный файл с уникальным именем.
    """
    # Читаем файл по частям чтобы не грузить в память целиком
    hasher = hashlib.md5()
    for chunk in file.chunks():
        hasher.update(chunk)
    
    file.seek(0)  # Сбрасываем указатель
    
    # Генерируем уникальное имя
    file_extension = os.path.splitext(file.name)[1]
    unique_filename = f"{hasher.hexdigest()}{file_extension}"
    
    # Сохраняем файл
    path = os.path.join(upload_to, unique_filename)
    saved_path = default_storage.save(path, ContentFile(file.read()))
    
    return saved_path


def format_file_size(size_bytes):
    """
    Форматирует размер файла в читаемый вид.
    """
    if not size_bytes:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"