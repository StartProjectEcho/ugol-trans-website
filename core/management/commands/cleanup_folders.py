# core/management/commands/cleanup_folders.py
from django.core.management.base import BaseCommand
from core.signals import cleanup_empty_folders


class Command(BaseCommand):
    help = 'Очистка пустых папок в медиа-директории'
    
    def handle(self, *args, **options):
        self.stdout.write("Очистка пустых папок в медиа-директории...")
        cleanup_empty_folders()
        self.stdout.write(self.style.SUCCESS("Очистка завершена"))