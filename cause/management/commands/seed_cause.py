from django.core.management.base import BaseCommand
from cause.models import Cause
from datetime import datetime, timezone
import random

class Command(BaseCommand):
    help = 'Seeds the database with sample causes'

    def add_arguments(self, parser):
        parser.add_argument('--number', type=int, default=10, help='Number of causes to create')

    def handle(self, *args, **options):
        number = options['number']
        self.stdout.write(f'Seeding {number} causes...')
        
        causes = [
            {'name': 'Technical Issue', 'description': 'Problems related to technical errors.'},
            {'name': 'User Error', 'description': 'Mistakes made by users.'},
            {'name': 'External Factor', 'description': 'Issues caused by external factors.'},
            {'name': 'Network Problem', 'description': 'Issues related to network connectivity.'},
            {'name': 'Hardware Failure', 'description': 'Failures in hardware components.'},
            {'name': 'Software Bug', 'description': 'Bugs in software applications.'},
            {'name': 'Configuration Error', 'description': 'Errors in system configuration.'},
            {'name': 'Security Breach', 'description': 'Security-related incidents.'},
            {'name': 'Performance Issue', 'description': 'Issues affecting system performance.'},
            {'name': 'Compatibility Problem', 'description': 'Problems with software compatibility.'}
        ]
        
        # Create random number of causes
        selected_causes = random.sample(causes, min(number, len(causes)))
        
        for c in selected_causes:
            Cause.objects.get_or_create(
                name=c['name'],
                defaults={
                    'description': c['description'],
                    'created_at': datetime.now(timezone.utc)
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(selected_causes)} causes')) 