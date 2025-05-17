from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime
import random
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            type=int,
            default=5,
            help='Number of items to create for each model'
        )
        parser.add_argument(
            '--staging',
            action='store_true',
            help='Seed staging-specific data'
        )
        parser.add_argument(
            '--production',
            action='store_true',
            help='Seed production-specific data'
        )

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        # Create admin user if it doesn't exist
        if not User.objects.filter(email='admin@example.com').exists():
            User.objects.create_superuser(
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Create regular users
        for i in range(options['number']):
            email = f'user{i}@example.com'
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    email=email,
                    password='password123',
                    first_name=f'Test{i}',
                    last_name=f'User{i}',
                    role='user'
                )
                self.stdout.write(self.style.SUCCESS(f'Created user {email}'))

        # Create test data for other models if they exist
        try:
            from cause.models import Cause
            for i in range(options['number']):
                Cause.objects.create(
                    title=f'Test Cause {i}',
                    description=f'Description for cause {i}',
                    created_at=timezone.now(),
                    updated_at=timezone.now()
                )
                self.stdout.write(self.style.SUCCESS(f'Created cause {i}'))
        except ImportError:
            pass

        try:
            from question.models import Question
            for i in range(options['number']):
                Question.objects.create(
                    title=f'Test Question {i}',
                    question=f'Content for question {i}',
                    mode='PRIBADI',
                    created_at=timezone.now(),
                    user=User.objects.first()
                )
                self.stdout.write(self.style.SUCCESS(f'Created question {i}'))
        except ImportError:
            pass

        try:
            from tag.models import Tag
            for i in range(options['number']):
                Tag.objects.create(
                    name=f'Tag {i}',
                    description=f'Description for tag {i}'
                )
                self.stdout.write(self.style.SUCCESS(f'Created tag {i}'))
        except ImportError:
            pass

        self.stdout.write(self.style.SUCCESS('Successfully seeded data')) 