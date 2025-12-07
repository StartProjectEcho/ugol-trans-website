"""
Сигналы для приложения core.
"""
import os
import shutil
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Image, File
import logging

logger = logging.getLogger(__name__)


def delete_empty_parent_folders(file_path):
    """
    Рекурсивно удаляет пустые родительские папки.
    
    Args:
        file_path: Путь к удаленному файлу
    """
    try:
        if not file_path:
            return
            
        # Получаем директорию файла
        directory = os.path.dirname(file_path)
        
        # Поднимаемся вверх по директориям и удаляем пустые
        while directory and os.path.exists(directory):
            # Проверяем, пуста ли директория
            if not os.listdir(directory):
                try:
                    os.rmdir(directory)
                    logger.info(f"Удалена пустая директория: {directory}")
                except OSError as e:
                    logger.warning(f"Не удалось удалить директорию {directory}: {e}")
                    break
            else:
                # Директория не пуста, останавливаемся
                break
            
            # Поднимаемся на уровень выше
            directory = os.path.dirname(directory)
            
            # Останавливаемся, если достигли корневой медиа-директории
            if 'media' in directory and not any(
                x in directory for x in ['images', 'files']
            ):
                break
                
    except Exception as e:
        logger.error(f"Ошибка при удалении пустых папок: {e}")


@receiver(post_delete, sender=Image)
def delete_image_file(sender, instance, **kwargs):
    """
    Удаление файла изображения при удалении записи из БД.
    """
    if instance.image:
        try:
            # Получаем путь к файлу
            file_path = instance.image.path if hasattr(instance.image, 'path') else None
            
            # Удаляем физический файл
            if file_path and os.path.isfile(file_path):
                os.remove(file_path)
                logger.info(f"Удален файл изображения: {file_path}")
                
                # Удаляем пустые родительские папки
                delete_empty_parent_folders(file_path)
                
        except (ValueError, OSError, AttributeError) as e:
            logger.error(f"Ошибка удаления файла изображения: {e}")


@receiver(post_delete, sender=File)
def delete_file_file(sender, instance, **kwargs):
    """
    Удаление файла при удалении записи из БД.
    """
    if instance.file:
        try:
            # Получаем путь к файлу
            file_path = instance.file.path if hasattr(instance.file, 'path') else None
            
            # Удаляем физический файл
            if file_path and os.path.isfile(file_path):
                os.remove(file_path)
                logger.info(f"Удален файл: {file_path}")
                
                # Удаляем пустые родительские папки
                delete_empty_parent_folders(file_path)
                
        except (ValueError, OSError, AttributeError) as e:
            logger.error(f"Ошибка удаления файла: {e}")


@receiver(pre_save, sender=Image)
def delete_old_image_on_update(sender, instance, **kwargs):
    """
    Удаление старого файла при обновлении изображения.
    """
    if not instance.pk:
        return
    
    try:
        old_instance = sender.objects.get(pk=instance.pk)
        # Если изображение изменилось
        if old_instance.image and old_instance.image != instance.image:
            try:
                file_path = old_instance.image.path if hasattr(old_instance.image, 'path') else None
                if file_path and os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.info(f"Удален старый файл изображения при обновлении: {file_path}")
                    
                    # Удаляем пустые родительские папки
                    delete_empty_parent_folders(file_path)
                    
            except (ValueError, OSError, AttributeError):
                pass  # Игнорируем ошибки удаления
    except sender.DoesNotExist:
        pass


@receiver(pre_save, sender=File)
def delete_old_file_on_update(sender, instance, **kwargs):
    """
    Удаление старого файла при обновлении.
    """
    if not instance.pk:
        return
    
    try:
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance.file and old_instance.file != instance.file:
            try:
                file_path = old_instance.file.path if hasattr(old_instance.file, 'path') else None
                if file_path and os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.info(f"Удален старый файл при обновлении: {file_path}")
                    
                    # Удаляем пустые родительские папки
                    delete_empty_parent_folders(file_path)
                    
            except (ValueError, OSError, AttributeError):
                pass
    except sender.DoesNotExist:
        pass


# Дополнительный сигнал для очистки пустых папок при запуске (опционально)
def cleanup_empty_folders():
    """
    Очистка всех пустых папок в медиа-директории.
    Вызывать вручную при необходимости.
    """
    from django.conf import settings
    import os
    
    media_root = settings.MEDIA_ROOT
    
    def remove_empty_dirs(path):
        """Рекурсивно удаляет пустые директории."""
        if not os.path.isdir(path):
            return False
            
        # Проверяем все поддиректории
        has_files = False
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                if remove_empty_dirs(item_path):
                    has_files = True
            else:
                has_files = True
        
        # Если директория пуста и не является корневой медиа-директорией
        if not has_files and path != media_root:
            try:
                os.rmdir(path)
                logger.info(f"Очистка: удалена пустая директория {path}")
                return False
            except OSError as e:
                logger.warning(f"Очистка: не удалось удалить {path}: {e}")
                return True
                
        return has_files
    
    # Запускаем очистку
    logger.info("Начата очистка пустых папок в медиа-директории")
    remove_empty_dirs(media_root)
    logger.info("Очистка пустых папок завершена")