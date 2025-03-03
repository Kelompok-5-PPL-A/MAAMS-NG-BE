from django.test import TestCase, Client
from django.urls import reverse
from .models import Question

class QuestionTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.test_email = 'test@example.com'
        self.question = Question.objects.create(
            user_email=self.test_email,
            content='Test Content'
        )

    def test_create_question_success(self):
        """Positive test: Question creation with valid data"""
        response = self.client.post(
            reverse('create_question'),
            {
                'user_email': self.test_email,
                'content': 'New Question Content'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertEqual(Question.objects.count(), 2)
        new_question = Question.objects.last()
        self.assertEqual(new_question.user_email, self.test_email)
        self.assertEqual(new_question.content, 'New Question Content')

    def test_create_question_invalid_email(self):
        """Negative test: Question creation with invalid email"""
        response = self.client.post(
            reverse('create_question'),
            {
                'user_email': 'invalid-email',
                'content': 'New Question Content'
            }
        )
        self.assertEqual(response.status_code, 200)  # Return to form
        self.assertEqual(Question.objects.count(), 1)  # No new question created

    def test_create_question_empty_content(self):
        """Negative test: Question creation with empty content"""
        response = self.client.post(
            reverse('create_question'),
            {
                'user_email': self.test_email,
                'content': ''
            }
        )
        self.assertEqual(response.status_code, 200)  # Return to form
        self.assertEqual(Question.objects.count(), 1)  # No new question created

    def test_view_question_success(self):
        """Positive test: View existing question"""
        response = self.client.get(
            reverse('view_question', args=[self.question.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Content')
        self.assertContains(response, self.test_email)

    def test_view_question_not_found(self):
        """Negative test: View non-existent question"""
        response = self.client.get(
            reverse('view_question', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_create_question_missing_fields(self):
        """Negative test: Question creation with missing fields"""
        response = self.client.post(
            reverse('create_question'),
            {}  # Empty data
        )
        self.assertEqual(response.status_code, 200)  # Return to form
        self.assertEqual(Question.objects.count(), 1)  # No new question created

    def test_question_str_representation(self):
        """Positive test: Question string representation"""
        expected_str = f"Question {self.question.id} by {self.test_email}"
        self.assertEqual(str(self.question), expected_str)

    def test_question_created_at_auto_set(self):
        """Positive test: Created_at field is automatically set"""
        new_question = Question.objects.create(
            user_email=self.test_email,
            content='Another Test Content'
        )
        self.assertIsNotNone(new_question.created_at)