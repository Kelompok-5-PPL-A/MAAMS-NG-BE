from django.test import TestCase, Client
from django.urls import reverse
from .models import Problem

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