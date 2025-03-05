from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import Problem
from .forms import QuestionForm
import uuid

class ProblemModelTests(TestCase):
    def test_problem_creation(self):
        """Positive test: Create a Problem instance with default status"""
        problem = Problem.objects.create(
            user_email='test@example.com',
            question='Test question content'
        )
        self.assertEqual(problem.user_email, 'test@example.com')
        self.assertEqual(problem.question, 'Test question content')
        self.assertIsNotNone(problem.id)  # Check UUID is generated
        self.assertIsNotNone(problem.created_at)

    def test_problem_creation_with_status(self):
        """Positive test: Create a Problem instance with specific status"""
        problem = Problem.objects.create(
            user_email='test@example.com',
            question='Test question content',
            status='PENGAWASAN'
        )
        self.assertEqual(problem.status, 'PENGAWASAN')

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
            problem = Problem(
                user_email='invalid-email',
                question='Test question content'
            )
            problem.full_clean()

    def test_problem_creation_empty_question(self):
        """Negative test: Create a Problem instance with empty question"""
        with self.assertRaises(ValidationError):
            problem = Problem(
                user_email='test@example.com',
                question=''
            )
            problem.full_clean()

    def test_problem_creation_missing_fields(self):
        """Negative test: Create a Problem instance with missing fields"""
        with self.assertRaises(ValidationError):
            problem = Problem(
                user_email='test@example.com'
            )
            problem.full_clean()

    def test_problem_creation_invalid_status(self):
        """Negative test: Create a Problem instance with invalid status"""
        with self.assertRaises(ValidationError):
            problem = Problem(
                user_email='test@example.com',
                question='Test question content',
                status='INVALID_STATUS'
            )
            problem.full_clean()

    def test_problem_id_is_uuid(self):
        """Positive test: Problem ID is UUID and auto-generated"""
        problem = Problem.objects.create(
            user_email='test@example.com',
            question='Test question content'
        )
        self.assertIsInstance(problem.id, uuid.UUID)
        self.assertIsNotNone(problem.id)

class QuestionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.submit_url = reverse('submit_question')
        self.success_url = reverse('success')
        self.test_email = 'test@example.com'
        self.test_question = 'Test question content'
        self.remove_url = reverse('remove_question', kwargs={'question_id': uuid.uuid4()})  # Placeholder for a UUID

    def test_submit_question_success(self):
        """Positive test: Submit question with valid data"""
        response = self.client.post(self.submit_url, {
            'user_email': self.test_email,
            'question': self.test_question
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Problem.objects.count(), 1)  # Check that the question was created

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

    def test_remove_question_success(self):
        """Positive test: Remove a question successfully"""
        problem = Problem.objects.create(
            user_email='test@example.com',
            question='Test question content'
        )
        response = self.client.get(reverse('remove_question', kwargs={'question_id': problem.id}))
        self.assertEqual(response.status_code, 302)  # Redirect after removal
        self.assertRedirects(response, reverse('remove_success'))
        self.assertEqual(Problem.objects.count(), 0)  # Check that the question was removed

    def test_remove_question_not_found(self):
        """Negative test: Attempt to remove a question that does not exist"""
        response = self.client.get(reverse('remove_question', kwargs={'question_id': uuid.uuid4()}))
        self.assertEqual(response.status_code, 404)  # Should return 404 for non-existent question

    def test_success_page(self):
        """Test the success page"""
        response = self.client.get(self.success_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your question has been successfully submitted!")

    def test_remove_success_page(self):
        """Test the remove success page"""
        response = self.client.get(reverse('remove_success'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The question has been successfully removed!")