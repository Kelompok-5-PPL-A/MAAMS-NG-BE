from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from question.models import Question
from tag.models import Tag
from datetime import datetime, timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample questions'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding questions...')
        
        # Create sample tags if they don't exist
        tags = ['Python', 'Django', 'React', 'JavaScript', 'TypeScript', 'Docker', 'AWS', 'CI/CD']
        tag_objects = []
        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tag_objects.append(tag)
        
        # Create sample questions
        questions = [
            {
                'title': 'How to use Django ORM?',
                'question': 'What are the best practices for using Django ORM?',
                'mode': Question.ModeChoices.PRIBADI,
                'tags': ['Python', 'Django']
            },
            {
                'title': 'React Hooks Tutorial',
                'question': 'Can someone explain React Hooks in detail?',
                'mode': Question.ModeChoices.PENGAWASAN,
                'tags': ['React', 'JavaScript']
            },
            {
                'title': 'Docker Best Practices',
                'question': 'What are the best practices for Docker containerization?',
                'mode': Question.ModeChoices.PRIBADI,
                'tags': ['Docker', 'AWS']
            },
            {
                'title': 'TypeScript vs JavaScript',
                'question': 'What are the key differences between TypeScript and JavaScript?',
                'mode': Question.ModeChoices.PRIBADI,
                'tags': ['TypeScript', 'JavaScript']
            },
            {
                'title': 'AWS Lambda Functions',
                'question': 'How do I create and deploy AWS Lambda functions?',
                'mode': Question.ModeChoices.PENGAWASAN,
                'tags': ['AWS', 'Docker']
            },
            {
                'title': 'CI/CD Pipeline Setup',
                'question': 'What are the best practices for setting up a CI/CD pipeline?',
                'mode': Question.ModeChoices.PRIBADI,
                'tags': ['CI/CD', 'Docker']
            },
            {
                'title': 'Kubernetes Basics',
                'question': 'Can someone explain the basics of Kubernetes?',
                'mode': Question.ModeChoices.PENGAWASAN,
                'tags': ['Kubernetes', 'Docker']
            },
            {
                'title': 'Microservices Architecture',
                'question': 'What are the best practices for designing microservices?',
                'mode': Question.ModeChoices.PRIBADI,
                'tags': ['Microservices', 'Docker']
            },
            {
                'title': 'Python Async Programming',
                'question': 'How do I use async/await in Python?',
                'mode': Question.ModeChoices.PENGAWASAN,
                'tags': ['Python']
            },
            {
                'title': 'React Performance Optimization',
                'question': 'What are the best practices for optimizing React performance?',
                'mode': Question.ModeChoices.PRIBADI,
                'tags': ['React', 'JavaScript']
            }
        ]
        
        # Get or create a test user
        user, _ = User.objects.get_or_create(
            username='testuser',
            email='test@example.com',
            defaults={
                'password': 'testpass123',
                'is_active': True
            }
        )
        
        # Create questions
        for q_data in questions:
            question = Question.objects.create(
                title=q_data['title'],
                question=q_data['question'],
                mode=q_data['mode'],
                user=user,
                created_at=datetime.now(timezone.utc)
            )
            
            # Add tags
            for tag_name in q_data['tags']:
                tag = Tag.objects.get(name=tag_name)
                question.tags.add(tag)
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded questions')) 