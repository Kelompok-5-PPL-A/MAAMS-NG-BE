from question.models import Question
from cause.models import Causes
from .base_seeder import BaseSeeder

class Command(BaseSeeder):
    help = 'Seeds the database with initial causes'

    def seed(self):
        # Get questions to associate with causes
        questions = Question.objects.filter(title__in=[
            'Economic Impact',
            'Social Media',
            'Tech Education'
        ])

        for question in questions:
            # Create 3 causes for each question
            for i in range(3):
                Causes.objects.create(
                    question=question,
                    row=i + 1,
                    column=1,
                    mode=question.mode,
                    cause=f'Cause {i + 1} for {question.title}',
                    status=False,
                    root_status=False,
                    feedback=''
                )
                self.stdout.write(self.style.SUCCESS(f'Created cause for question: {question.title}'))

    def undo_seed(self):
        # Get the questions
        questions = Question.objects.filter(title__in=[
            'Economic Impact',
            'Social Media',
            'Tech Education'
        ])
        
        # Delete all causes associated with these questions
        Causes.objects.filter(question__in=questions).delete()
        self.stdout.write(self.style.SUCCESS('Removed seeded causes')) 