from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import Problem

class ProblemModelTests(TestCase):
    def test_problem_creation(self):
        """Positive test: Create a Problem instance"""
        problem = Problem.objects.create(
            user_email='test@example.com',
            question='Test question content'
        )
        self.assertEqual(problem.user_email, 'test@example.com')
        self.assertEqual(problem.question, 'Test question content')
        self.assertIsNotNone(problem.created_at)

    def test_problem_str_representation(self):
        """Positive test: String representation of Problem"""
        problem = Problem.objects.create(
            user_email='test@example.com',
            question='Test question content'
        )
        self.assertEqual(str(problem), 'Test question content')

    def test_problem_creation_invalid_email(self):
        """Negative test: Create a Problem instance with invalid email"""
        with self.assertRaises(ValidationError):
            Problem.objects.create(
                user_email='invalid-email',
                question='Test question content'
            )

    def test_problem_creation_empty_question(self):
        """Negative test: Create a Problem instance with empty question"""
        with self.assertRaises(ValidationError):
            Problem.objects.create(
                user_email='test@example.com',
                question=''
            )

    def test_problem_creation_missing_fields(self):
        """Negative test: Create a Problem instance with missing fields"""
        with self.assertRaises(ValidationError):
            Problem.objects.create(
                user_email='test@example.com'
            )

class QuestionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.submit_url = reverse('submit_question')
        self.success_url = reverse('success')
        self.test_email = 'test@example.com'
        self.test_question = 'Test question content'

    def test_submit_question_success(self):
        """Positive test: Submit question with valid data"""
        response = self.client.post(self.submit_url, {
            'user_email': self.test_email,
            'question': self.test_question
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Problem.objects.count(), 1)
        new_problem = Problem.objects.last()
        self.assertEqual(new_problem.user_email, self.test_email)
        self.assertEqual(new_problem.question, self.test_question)

    def test_submit_question_invalid_email(self):
        """Negative test: Submit question with invalid email"""
        response = self.client.post(self.submit_url, {
            'user_email': 'invalid-email',
            'question': self.test_question
        })
        self.assertEqual(response.status_code, 200)  # Return to form
        self.assertContains(response, 'There are some issues with your submission')
        self.assertEqual(Problem.objects.count(), 0)  # No new problem created

    def test_submit_question_empty_question(self):
        """Negative test: Submit question with empty question"""
        response = self.client.post(self.submit_url, {
            'user_email': self.test_email,
            'question': ''
        })
        self.assertEqual(response.status_code, 200)  # Return to form
        self.assertContains(response, 'There are some issues with your submission')
        self.assertEqual(Problem.objects.count(), 0)  # No new problem created

    def test_submit_question_missing_fields(self):
        """Negative test: Submit question with missing fields"""
        response = self.client.post(self.submit_url, {})
        self.assertEqual(response.status_code, 200)  # Return to form
        self.assertContains(response, 'There are some issues with your submission')
        self.assertEqual(Problem.objects.count(), 0)  # No new problem created