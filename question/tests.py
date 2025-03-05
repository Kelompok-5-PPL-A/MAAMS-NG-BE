from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import Problem
import uuid

class ProblemModelTests(TestCase):
    def test_problem_creation(self):
        """Positive test: Create a Problem instance with default values"""
        problem = Problem.objects.create(
            user_email='test@example.com'
        )
        self.assertEqual(problem.user_email, 'test@example.com')
        self.assertEqual(problem.title, 'N/A')  # Check default value
        self.assertEqual(problem.question, 'N/A')  # Check default value
        self.assertEqual(problem.status, 'PRIBADI') # Check default status
        self.assertIsNotNone(problem.created_at)
        self.assertIsInstance(problem.id, uuid.UUID)

    def test_problem_creation_with_status(self):
        """Positive test: Create a Problem instance with specific status"""
        problem = Problem.objects.create(
            user_email='test@example.com',
            title='Test Title',
            question='Test question content',
            status='PENGAWASAN'
        )
        self.assertEqual(problem.status, 'PENGAWASAN')

    def test_problem_creation_invalid_email(self):
        """Negative test: Create a Problem instance with invalid email"""
        with self.assertRaises(ValidationError):
            problem = Problem(
                user_email='invalid-email',
                title='Test Title',
                question='Test question content'
            )
            problem.full_clean()

    def test_problem_creation_empty_title(self):
        """Negative test: Create a Problem instance with empty title"""
        with self.assertRaises(ValidationError):
            problem = Problem(
                user_email='test@example.com',
                title='',
                question='Test question content'
            )
            problem.full_clean()

    def test_problem_creation_empty_question(self):
        """Negative test: Create a Problem instance with empty question"""
        with self.assertRaises(ValidationError):
            problem = Problem(
                user_email='test@example.com',
                title='Test Title',
                question=''
            )
            problem.full_clean()

    def test_problem_creation_invalid_status(self):
        """Negative test: Create a Problem instance with invalid status"""
        with self.assertRaises(ValidationError):
            problem = Problem(
                user_email='test@example.com',
                title='Test Title',
                question='Test question content',
                status='INVALID_STATUS'
            )
            problem.full_clean()

    def test_problem_creation_with_custom_values(self):
        """Positive test: Create a Problem instance with custom values"""
        problem = Problem.objects.create(
            user_email='test@example.com',
            title='Test Title',
            question='Test question content'
        )
        self.assertEqual(problem.title, 'Test Title')
        self.assertEqual(problem.question, 'Test question content')

class QuestionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.submit_url = reverse('submit_question')
        self.success_url = reverse('success')
        self.test_email = 'test@example.com'
        self.test_title = 'Test Title'
        self.test_question = 'Test question content'

    def test_submit_question_success(self):
        """Positive test: Submit question with valid data"""
        response = self.client.post(self.submit_url, {
            'title': self.test_title,
            'question': self.test_question,
            'status': 'PRIBADI'
        })
        self.assertEqual(response.status_code, 200)
        new_problem = Problem.objects.filter(
            title=self.test_title,
            question=self.test_question,
            status='PRIBADI'
        ).first()
        self.assertIsNotNone(new_problem)
        self.assertEqual(new_problem.title, self.test_title)
        self.assertEqual(new_problem.question, self.test_question)
        self.assertEqual(new_problem.status, 'PRIBADI')

    def test_submit_question_with_pengawasan_status(self):
        """Positive test: Submit question with PENGAWASAN status"""
        response = self.client.post(self.submit_url, {
            'title': self.test_title,
            'question': self.test_question,
            'status': 'PENGAWASAN'
        })
        self.assertEqual(response.status_code, 200)
        new_problem = Problem.objects.last()
        self.assertEqual(new_problem.status, 'PENGAWASAN')

    def test_submit_question_empty_title(self):
        """Negative test: Submit question with empty title"""
        response = self.client.post(self.submit_url, {
            'title': '',
            'question': self.test_question,
            'status': 'PRIBADI'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are some issues with your submission')
        self.assertEqual(Problem.objects.count(), 0)

    def test_submit_question_empty_question(self):
        """Negative test: Submit question with empty question"""
        response = self.client.post(self.submit_url, {
            'title': self.test_title,
            'question': '',
            'status': 'PRIBADI'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are some issues with your submission')
        self.assertEqual(Problem.objects.count(), 0)

    def test_submit_question_invalid_status(self):
        """Negative test: Submit question with invalid status"""
        response = self.client.post(self.submit_url, {
            'title': self.test_title,
            'question': self.test_question,
            'status': 'INVALID'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are some issues with your submission')
        self.assertEqual(Problem.objects.count(), 0)

    def test_submit_question_missing_fields(self):
        """Corner case: Submit question with missing fields"""
        response = self.client.post(self.submit_url, {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are some issues with your submission')
        self.assertEqual(Problem.objects.count(), 0)

    def test_submit_question_extra_long_title(self):
        """Corner case: Submit question with title exceeding max length"""
        response = self.client.post(self.submit_url, {
            'title': 'a' * 256,  # Exceeds max_length=255
            'question': self.test_question,
            'status': 'PRIBADI'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are some issues with your submission')
        self.assertEqual(Problem.objects.count(), 0)

    def test_submit_question_with_defaults(self):
        """Positive test: Submit question with default values"""
        response = self.client.post(self.submit_url, {
            'user_email': self.test_email
        })
        self.assertEqual(response.status_code, 200)
        new_problem = Problem.objects.last()
        self.assertEqual(new_problem.title, 'N/A')
        self.assertEqual(new_problem.question, 'N/A')
        self.assertEqual(new_problem.status, 'PRIBADI')