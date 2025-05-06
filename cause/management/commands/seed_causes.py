from django.core.management.base import BaseCommand
from question.models import Question
from cause.models import Causes
import uuid
import random

class Command(BaseCommand):
    help = 'Seed the Causes model with minimal data for local development'

    def add_arguments(self, parser):
        parser.add_argument('--number', type=int, default=100, help='Number of causes to create')

    def handle(self, *args, **options):
        number = options['number']
        self.stdout.write(self.style.SUCCESS(f'Seeding {number} causes...'))
        
        # First, make sure we have some questions to link to
        if Question.objects.count() == 0:
            self.stdout.write(self.style.WARNING('No questions found. Creating a sample question...'))
            question = Question.objects.create(title="Sample Question", description="This is a sample question for testing")
        else:
            question = Question.objects.first()
        
        # Create causes
        for i in range(number):
            row = i // 3  # Simple grid layout for the causes
            column = i % 3
            mode = random.choice([Causes.ModeChoices.PRIBADI, Causes.ModeChoices.PENGAWASAN])
            
            Causes.objects.create(
                id=uuid.uuid4(),
                question=question,
                row=row,
                column=column,
                mode=mode,
                cause=f"Sample cause {i+1}",
                status=bool(random.getrandbits(1)),
                root_status=bool(random.getrandbits(1)),
                feedback=""
            )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {number} causes'))