from django.core.management.base import BaseCommand
from tag.models import Tag
from .base_seeder import BaseSeeder

class Command(BaseSeeder):
    help = 'Seeds the database with initial tags'

    def seed(self):
        tags = [
            'economy',  
            'climate',  
            'social',    
            'tech',
            'health',    
            'edu',
            'politics',
            'culture'   
        ]

        for tag_name in tags:
            _, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created tag: {tag_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Tag already exists: {tag_name}'))

    def undo_seed(self):
        Tag.objects.filter(name__in=[
            'economy',
            'climate',
            'social',
            'tech',
            'health',
            'edu',
            'politics',
            'culture'
        ]).delete()
        self.stdout.write(self.style.SUCCESS('Removed seeded tags')) 