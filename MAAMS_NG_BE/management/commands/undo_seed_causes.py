from django.core.management.base import BaseCommand
from question.models import Question
from cause.models import Causes

class Command(BaseCommand):
    help = 'Undoes causes seeding'

    def handle(self, *args, **options):
        try:
            # Get the questions
            questions = Question.objects.filter(title__in=[
                'Economic Impact',
                'Social Media',
                'Tech Education'
            ])
            
            # Delete all causes associated with these questions
            Causes.objects.filter(question__in=questions).delete()
            self.stdout.write(self.style.SUCCESS('Successfully removed seeded causes'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error removing seeded causes: {str(e)}'))
            raise 