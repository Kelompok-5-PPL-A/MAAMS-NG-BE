from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, Mock
from models import Question
from tag.models import Tag

class TestQuestionPostView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/question/submit/'
        self.valid_payload = {
            'title': 'Test Titles',
            'question': 'Test Question',
            'mode': Question.ModeChoices.PRIBADI,
            'tags': ['tag1', 'tag2']
        }

    def test_create_question_success(self):
        # Arrange
        mock_question = Mock(spec=Question)
        mock_question.id = '123e4567-e89b-12d3-a456-426614174000'
        mock_question.title = self.valid_payload['title']
        mock_question.question = self.valid_payload['question']
        mock_question.mode = self.valid_payload['mode']
        mock_question.tags.all.return_value = [
            Mock(spec=Tag, name=tag) for tag in self.valid_payload['tags']
        ]

        with patch('services.QuestionService.create') as mock_create:
            mock_create.return_value = mock_question
            
            # Act
            response = self.client.post(
                self.url,
                data=self.valid_payload,
                format='json'
            )

            # Assert
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['title'], self.valid_payload['title'])
            mock_create.assert_called_once_with(**self.valid_payload)

    def test_create_question_invalid_title(self):
        # Arrange
        invalid_payload = {
            'title': '',
            'question': 'Test Question',
            'mode': Question.ModeChoices.PRIBADI,
            'tags': ['tag1']
        }

        # Act
        response = self.client.post(
            self.url,
            data=invalid_payload,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_question_invalid_question(self):
        # Arrange
        invalid_payload = {
            'title': 'Test Title',
            'question': '',
            'mode': Question.ModeChoices.PRIBADI,
            'tags': ['tag1']
        }

        # Act
        response = self.client.post(
            self.url,
            data=invalid_payload,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_question_invalid_mode(self):
        # Arrange
        invalid_payload = {
            'title': 'Test Title',
            'question': 'Test Question',
            'mode': 'INVALID_MODE',
            'tags': ['tag1']
        }

        # Act
        response = self.client.post(
            self.url,
            data=invalid_payload,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_question_missing_required_fields(self):
        # Arrange
        incomplete_payload = {
            'title': 'Test Title'
        }

        # Act
        response = self.client.post(
            self.url,
            data=incomplete_payload,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_question_service_error(self):
        # Arrange
        with patch('services.QuestionService.create') as mock_create:
            mock_create.side_effect = Exception('Service error')
            
            # Act
            response = self.client.post(
                self.url,
                data=self.valid_payload,
                format='json'
            )

            # Assert
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)