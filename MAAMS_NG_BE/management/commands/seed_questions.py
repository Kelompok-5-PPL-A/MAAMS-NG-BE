from django.contrib.auth import get_user_model
from question.models import Question
from tag.models import Tag
from .base_seeder import BaseSeeder

User = get_user_model()

class Command(BaseSeeder):
    help = 'Seeds the database with initial questions'

    def seed(self):
        # Get or create a test user
        user, _ = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'username': 'testuser',
                'password': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )

        # Create sample questions
        questions = [
            {
                'title': 'Economic Impact',
                'question': 'What are the economic impacts of climate change?',
                'mode': Question.ModeChoices.PENGAWASAN,
                'user': user,
                'tags': ['economy', 'climate']
            },
            {
                'title': 'Social Media',
                'question': 'How does social media affect mental health?',
                'mode': Question.ModeChoices.PRIBADI,
                'user': user,
                'tags': ['social', 'tech']
            },
            {
                'title': 'Tech Education',
                'question': 'What are the best ways to learn programming?',
                'mode': Question.ModeChoices.PENGAWASAN,
                'user': user,
                'tags': ['tech', 'edu']
            }
        ]

        for q_data in questions:
            question, created = Question.objects.get_or_create(
                title=q_data['title'],
                defaults={
                    'question': q_data['question'],
                    'mode': q_data['mode'],
                    'user': q_data['user']
                }
            )
            
            # Add tags - create them if they don't exist
            for tag_name in q_data['tags']:
                tag, tag_created = Tag.objects.get_or_create(name=tag_name)
                if tag_created:
                    self.stdout.write(self.style.SUCCESS(f'Created tag: {tag_name}'))
                question.tags.add(tag)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created question: {question.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Question already exists: {question.title}'))

    def undo_seed(self):
        Question.objects.filter(title__in=[
            'Economic Impact',
            'Social Media',
            'Tech Education'
        ]).delete()
        self.stdout.write(self.style.SUCCESS('Removed seeded questions')) 