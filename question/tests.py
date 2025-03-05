from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import Problem
import uuid

class ProblemModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.valid_email = 'test@example.com'
        cls.valid_title = 'Test Title'
        cls.valid_question = 'Test question content'

    def test_problem_creation_with_defaults(self):
        """Menguji pembuatan instance Problem dengan nilai default"""
        problem = Problem.objects.create(user_email=self.valid_email)
        self.assertEqual(problem.user_email, self.valid_email)
        self.assertEqual(problem.title, 'N/A')
        self.assertEqual(problem.question, 'N/A')
        self.assertEqual(problem.status, 'PRIBADI')
        self.assertIsInstance(problem.id, uuid.UUID)

    def test_problem_creation_with_custom_values(self):
        """Menguji pembuatan instance Problem dengan nilai yang ditentukan"""
        problem = Problem.objects.create(
            user_email=self.valid_email,
            title=self.valid_title,
            question=self.valid_question,
            status='PENGAWASAN'
        )
        self.assertEqual(problem.title, self.valid_title)
        self.assertEqual(problem.question, self.valid_question)
        self.assertEqual(problem.status, 'PENGAWASAN')

    def test_invalid_email_raises_validation_error(self):
        """Menguji validasi email yang tidak valid"""
        with self.assertRaises(ValidationError):
            problem = Problem(user_email='invalid-email', title=self.valid_title, question=self.valid_question)
            problem.full_clean()

    def test_empty_title_raises_validation_error(self):
        """Menguji validasi title kosong"""
        with self.assertRaises(ValidationError):
            problem = Problem(user_email=self.valid_email, title='', question=self.valid_question)
            problem.full_clean()

    def test_empty_question_raises_validation_error(self):
        """Menguji validasi question kosong"""
        with self.assertRaises(ValidationError):
            problem = Problem(user_email=self.valid_email, title=self.valid_title, question='')
            problem.full_clean()

    def test_invalid_status_raises_validation_error(self):
        """Menguji validasi status yang tidak valid"""
        with self.assertRaises(ValidationError):
            problem = Problem(user_email=self.valid_email, title=self.valid_title, question=self.valid_question, status='INVALID')
            problem.full_clean()


class QuestionViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.submit_url = reverse('submit_question')
        cls.success_url = reverse('success')
        cls.valid_data = {
            'user_email': 'test@example.com',
            'title': 'Test Title',
            'question': 'Test Question',
            'status': 'PRIBADI'
        }

    def test_submit_question_success(self):
        """Menguji pengiriman form yang valid"""
        response = self.client.post(self.submit_url, self.valid_data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_submit_question_with_pengawasan_status(self):
        """Menguji pengiriman form dengan status PENGAWASAN"""
        data = self.valid_data.copy()
        data['status'] = 'PENGAWASAN'
        response = self.client.post(self.submit_url, data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_submit_question_empty_title_fails(self):
        """Menguji validasi title kosong"""
        data = self.valid_data.copy()
        data['title'] = ''
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)  # Form dikembalikan dengan error
        self.assertContains(response, 'This field is required.')
        self.assertEqual(Problem.objects.count(), 0)

    def test_submit_question_empty_question_fails(self):
        """Menguji validasi question kosong"""
        data = self.valid_data.copy()
        data['question'] = ''
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertEqual(Problem.objects.count(), 0)

    def test_submit_question_invalid_status_fails(self):
        """Menguji validasi status yang tidak valid"""
        data = self.valid_data.copy()
        data['status'] = 'INVALID'
        response = self.client.post(self.submit_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select a valid choice.')
        self.assertEqual(Problem.objects.count(), 0)

    def test_get_request_renders_form(self):
        """Menguji apakah GET request menampilkan form dengan benar"""
        response = self.client.get(self.submit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'submit_question.html')
        self.assertIn('form', response.context)
