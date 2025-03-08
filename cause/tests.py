from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from question.models import Problem
from cause.models import Causes
import uuid

class CausesModelTest(TestCase):
    def setUp(self):
        """
        Set up Problem object without user (Guest)
        """
        self.question_uuid = uuid.uuid4()

        self.question = Problem.objects.create(
            id=self.question_uuid,
            question='pertanyaan',
            status=Problem.STATUS_CHOICES[0][0]  # PRIBADI
        )

        """
        Set up Causes object
        """
        self.causes_uuid = uuid.uuid4()

        Causes.objects.create(
            problem=self.question,
            id=self.causes_uuid,
            row=1,
            column=1,
            mode=Causes.STATUS_CHOICES[0][0],  # PRIBADI
            cause='cause'
        )

    def test_causes(self):
        causes = Causes.objects.get(id=self.causes_uuid)
        self.assertIsNotNone(causes)
        self.assertEqual(causes.problem.id, self.question.id)
        self.assertEqual(causes.row, 1)
        self.assertEqual(causes.column, 1)
        self.assertEqual(causes.mode, Causes.STATUS_CHOICES[0][0])  # PRIBADI
        self.assertEqual(causes.cause, 'cause')

class CausesViewGuestTest(APITestCase):
    def setUp(self):
        """
        Set up required data for guest test cases
        """
        self.question_uuid1 = uuid.uuid4()
        self.question = Problem.objects.create(
            id=self.question_uuid1,
            question='pertanyaan',
            status=Problem.STATUS_CHOICES[0][0]  # PRIBADI
        )

        self.post_url = reverse('causes-create')  

    def test_guest_create_cause_positive(self):
        """Test guest can create cause successfully"""
        valid_data = {
            'question_id': str(self.question_uuid1),
            'cause': 'cause',
            'row': 1,
            'column': 1,
            'mode': Causes.STATUS_CHOICES[0][0]  # PRIBADI
        }
        response = self.client.post(self.post_url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['cause'], 'cause')

    def test_guest_create_cause_negative_missing_cause(self):
        """Test guest cannot create cause with missing required fields"""
        invalid_data = {
            'question_id': str(self.question_uuid1),
            'row': 1,
            'column': 1,
            'mode': Causes.STATUS_CHOICES[0][0]  # PRIBADI
        }
        response = self.client.post(self.post_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
