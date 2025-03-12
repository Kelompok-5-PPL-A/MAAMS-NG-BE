from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from question.models import Question
import uuid

class CausesViewGuestTest(APITestCase):
    def setUp(self):
        """
        Set Up objects
        """
        self.question_uuid1 = uuid.uuid4()
        self.question1 = Question.objects.create(
            id=self.question_uuid1,
            question='pertanyaan',
            mode=Question.ModeChoices.PRIBADI
        )

        self.post_url = reverse('validator:create_causes')
    
    def test_guest_create_cause_positive(self):
        """Test guest can create cause successfully"""
        valid_data = {
            'question_id': self.question_uuid1,
            'cause': 'cause',
            'row': 1,
            'column': 1,
            'mode': Question.ModeChoices.PRIBADI
        }
        response = self.client.post(self.post_url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['cause'], 'cause')
    
    def test_guest_create_cause_negative_missing_cause(self):
        """Test guest cannot create cause with missing required fields"""
        invalid_data = {'question_id': self.question_uuid1, 'row': 1, 'column': 1, 'mode': ''}
        response = self.client.post(self.post_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
