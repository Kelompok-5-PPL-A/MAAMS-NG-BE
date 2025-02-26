from django.test import TestCase

# Create your tests here.

from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from .models import Problem
from .forms import QuestionForm

class TestProblemModel(TestCase):
    def test_problem_model_not_exists(self):
        """Test should fail because Problem model exists"""
        with self.assertRaises(ObjectDoesNotExist):
            problem = Problem.objects.create(question="Test")
            
    def test_str_representation_fails(self):
        """Test should fail because __str__ is implemented"""
        problem = Problem.objects.create(question="Test")
        self.assertNotEqual(str(problem), "Test")

class TestQuestionForm(TestCase):
    def test_form_validation_fails(self):
        """Test should fail because form validation works"""
        form_data = {'question': 'Test question'}
        form = QuestionForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_empty_form_validation_passes(self):
        """Test should fail because empty form validation fails"""
        form_data = {'question': ''}
        form = QuestionForm(data=form_data)
        self.assertTrue(form.is_valid())

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()

    def test_show_detail_page_fails(self):
        """Test should fail because view works correctly"""
        response = self.client.get(reverse('show_detail_page'))
        self.assertEqual(response.status_code, 404)

    def test_create_question_fails(self):
        """Test should fail because question creation works"""
        response = self.client.post(
            reverse('create_question'),
            {'question': 'Test question'},
            follow=True
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Problem.objects.count(), 0)

    def test_success_view_fails(self):
        """Test should fail because success view works"""
        response = self.client.get(reverse('success_url'))
        self.assertEqual(response.status_code, 404)

    def test_error_view_fails(self):
        """Test should fail because error view works"""
        response = self.client.get(reverse('error_url'))
        self.assertEqual(response.status_code, 404)