from django.core.management.base import BaseCommand
from tag.models import Tag
from datetime import datetime, timezone
import random

class Command(BaseCommand):
    help = 'Seeds the database with sample tags'

    def add_arguments(self, parser):
        parser.add_argument('--number', type=int, default=10, help='Number of tags to create')

    def handle(self, *args, **options):
        number = options['number']
        self.stdout.write(f'Seeding {number} tags...')
        
        all_tags = [
            'Python', 'Django', 'React', 'JavaScript', 'TypeScript', 
            'Docker', 'AWS', 'CI/CD', 'Kubernetes', 'Microservices',
            'Important', 'Urgent', 'General', 'Bug', 'Feature',
            'Documentation', 'Security', 'Performance', 'Testing', 'Deployment'
        ]
        
        selected_tags = random.sample(all_tags, min(number, len(all_tags)))
        
        for tag_name in selected_tags:
            Tag.objects.get_or_create(
                name=tag_name,
                defaults={'created_at': datetime.now(timezone.utc)}
            )
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(selected_tags)} tags')) 