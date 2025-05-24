from django.core.management.base import BaseCommand
from question.models import Question

class Command(BaseCommand):
    help = 'Undoes the seeding of questions'

    def handle(self, *args, **options):
        try:
            # Delete seeded questions
            questions = Question.objects.filter(title__in=[
                'Economic Impact',
                'Social Media',
                'Tech Education'
            ])
            
            count = questions.count()
            questions.delete()
            
            self.stdout.write(self.style.SUCCESS(f'Successfully removed {count} seeded questions'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error unseeding questions: {str(e)}'))
            raise 