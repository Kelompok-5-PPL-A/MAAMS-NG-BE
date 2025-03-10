from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import Problem
from .forms import QuestionForm
import uuid

class ProblemModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.valid_email = 'test@example.com'
        cls.valid_title = 'Test Title'
        cls.valid_question = 'Test question content'
        cls.success_url = reverse('success')

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

    def test_str_representation(self):
        """Test the string representation of Problem model"""
        problem = Problem.objects.create(
            user_email=self.valid_email,
            title=self.valid_title,
            question=self.valid_question,
            status='PENGAWASAN'
        )
        self.assertEqual(str(problem), 'Test question content')
        
        # Test with different question content
        problem.question = 'Different question content'
        self.assertEqual(str(problem), 'Different question content')

    def test_remove_question_success(self):
        """Positive test: Remove a question successfully using POST method"""
        problem = Problem.objects.create(
            user_email='test@example.com',
            question='Test question content'
        )
        response = self.client.post(reverse('remove_question', kwargs={'question_id': problem.id}))
        self.assertEqual(response.status_code, 302)  # Redirect after removal
        self.assertRedirects(response, reverse('remove_success'))
        self.assertEqual(Problem.objects.count(), 0)  # Check that the question was removed

    def test_remove_question_get_method_not_allowed(self):
        """Test that GET requests to remove_question are not allowed"""
        problem = Problem.objects.create(
            user_email='test@example.com',
            question='Test question content'
        )
        response = self.client.get(reverse('remove_question', kwargs={'question_id': problem.id}))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
        self.assertEqual(Problem.objects.count(), 1)  # Question should not be removed

    def test_remove_question_not_found(self):
        """Negative test: Attempt to remove a question that does not exist"""
        response = self.client.post(reverse('remove_question', kwargs={'question_id': uuid.uuid4()}))
        self.assertEqual(response.status_code, 404)  # Should return 404 for non-existent question

    def test_success_page(self):
        """Test the success page with GET method"""
        response = self.client.get(self.success_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your question has been successfully submitted!")

    def test_success_page_post_not_allowed(self):
        """Test that POST requests to success page are not allowed"""
        response = self.client.post(self.success_url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_remove_success_page(self):
        """Test the remove success page with GET method"""
        response = self.client.get(reverse('remove_success'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The question has been successfully removed!")

    def test_remove_success_page_post_not_allowed(self):
        """Test that POST requests to remove_success page are not allowed"""
        response = self.client.post(reverse('remove_success'))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed


class QuestionViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.display_form_url = reverse('display_question_form')
        cls.process_form_url = reverse('process_question_form')
        cls.success_url = reverse('success')
        cls.valid_data = {
            'title': 'Test Title',
            'question': 'Test Question',
            'status': 'PRIBADI',
            'user_email': 'test@example.com'  # Add user_email
        }

    def test_display_question_form(self):
        """Test that GET request to display_question_form renders the form"""
        response = self.client.get(self.display_form_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'submit_question.html')
        self.assertIn('form', response.context)
    
    def test_display_question_form_post_not_allowed(self):
        """Test that POST requests to display_question_form are not allowed"""
        response = self.client.post(self.display_form_url, self.valid_data)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
        
    def test_process_question_form_success(self):
        """Test successful form submission"""
        response = self.client.post(self.process_form_url, self.valid_data)            
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.success_url)
        
        # Verify database entry
        self.assertEqual(Problem.objects.count(), 1)
        problem = Problem.objects.first()
        self.assertEqual(problem.title, self.valid_data['title'])
        self.assertEqual(problem.question, self.valid_data['question'])
        self.assertEqual(problem.status, self.valid_data['status'])

    def test_process_question_form_get_not_allowed(self):
        """Test that GET requests to process_question_form are not allowed"""
        response = self.client.get(self.process_form_url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_process_question_with_pengawasan_status(self):
        """Menguji pengiriman form dengan status PENGAWASAN"""
        data = self.valid_data.copy()
        data['status'] = 'PENGAWASAN'
        response = self.client.post(self.process_form_url, data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_process_question_empty_title_fails(self):
        """Menguji validasi title kosong"""
        data = self.valid_data.copy()
        data['title'] = ''
        response = self.client.post(self.process_form_url, data)
        self.assertEqual(response.status_code, 200)  # Form dikembalikan dengan error
        self.assertContains(response, 'This field is required.')
        self.assertEqual(Problem.objects.count(), 0)

    def test_process_question_empty_question_fails(self):
        """Menguji validasi question kosong"""
        data = self.valid_data.copy()
        data['question'] = ''
        response = self.client.post(self.process_form_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertEqual(Problem.objects.count(), 0)

    def test_process_question_invalid_status_fails(self):
        """Menguji validasi status yang tidak valid"""
        data = self.valid_data.copy()
        data['status'] = 'INVALID'
        response = self.client.post(self.process_form_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select a valid choice.')
        self.assertEqual(Problem.objects.count(), 0)

    def test_invalid_method_not_allowed(self):
        """Menguji bahwa metode HTTP yang tidak diizinkan akan ditolak"""
        response = self.client.put(self.process_form_url, self.valid_data)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed