from types import SimpleNamespace
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import CustomUser
from unittest.mock import patch, Mock
from question.models import Question
from question.serializers import QuestionResponse
from tag.models import Tag
from datetime import datetime
import uuid
from authentication.models import CustomUser

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
        self.user = CustomUser.objects.create_user(username='tester', email='test@example.com', password='test123')

    def test_create_question_success(self):
        # Arrange
        mock_question = Mock(spec=Question)
        mock_question.id = '123e4567-e89b-12d3-a456-426614174000'
        mock_question.title = self.valid_payload['title']
        mock_question.question = self.valid_payload['question']
        mock_question.mode = self.valid_payload['mode']
        mock_question.created_at = datetime.now().isoformat() + 'Z'
        mock_question.tags.all.return_value = [
            Tag(name=tag) for tag in self.valid_payload['tags']
        ]
        mock_question.user = self.user
        self.client.force_authenticate(user=self.user)


        with patch('question.services.QuestionService.create') as mock_create:
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
            mock_create.assert_called_once_with(
                title='Test Titles',
                question='Test Question',
                mode=Question.ModeChoices.PRIBADI,
                user=self.user,
                tags=['tag1', 'tag2']
            )


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
        with patch('question.services.QuestionService.create') as mock_create:
            mock_create.side_effect = Exception('Service error')
            # Act
            response = self.client.post(
                self.url,
                data=self.valid_payload,
                format='json'
            )

            # Assert
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def test_create_question_maximum_length_title(self):
        # Arrange
        payload = {
            'title': 'A' * 40,
            'question': 'Test Question',
            'mode': Question.ModeChoices.PRIBADI,
            'tags': ['tag1']
        }

        # Arrange
        mock_question = Mock(spec=Question)
        mock_question.id = '123e4567-e89b-12d3-a456-426614174921'
        mock_question.title = payload['title']
        mock_question.question = payload['question']
        mock_question.mode = payload['mode']
        mock_question.created_at = datetime.now().isoformat() + 'Z'
        mock_question.tags.all.return_value = [
            Tag(name=tag) for tag in payload['tags']
        ]

        mock_question.user = self.user
        self.client.force_authenticate(user=self.user)

        # Act
        response = self.client.post(
            self.url,
            data=payload,
            format='json'
        )

        with patch('question.services.QuestionService.create') as mock_create:
            mock_create.return_value = mock_question
            
            # Act
            response = self.client.post(
                self.url,
                data=payload,
                format='json'
            )

            # Assert
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['title'], payload['title'])
            mock_create.assert_called_once_with(**payload, user=self.user)
    

    def test_create_question_maximum_length_question(self):
        # Arrange
        payload = {
            'title': 'Test Title',
            'question': 'A' * 255,
            'mode': Question.ModeChoices.PRIBADI,
            'tags': ['tag1']
        }

        # Arrange
        mock_question = Mock(spec=Question)
        mock_question.id = '123e4567-e89b-12d3-a456-426614174921'
        mock_question.title = payload['title']
        mock_question.question = payload['question']
        mock_question.mode = payload['mode']
        mock_question.created_at = datetime.now().isoformat() + 'Z'
        mock_question.tags.all.return_value = [
            Tag(name=tag) for tag in payload['tags']
        ]
        mock_question.user = self.user
        self.client.force_authenticate(user=self.user)

        # Act
        response = self.client.post(
            self.url,
            data=payload,
            format='json'
        )

        with patch('question.services.QuestionService.create') as mock_create:      
            mock_create.return_value = mock_question
            
            # Act
            response = self.client.post(
                self.url,
                data=payload,
                format='json'
            )

            # Assert
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['title'], payload['title'])
            mock_create.assert_called_once_with(**payload, user=self.user)
    

class TestQuestionGet(TestCase):
    def setUp(self):
        # Create test tags
        self.tag1 = Tag.objects.create(name="test_tag1")
        self.tag2 = Tag.objects.create(name="test_tag2")
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='tester', email='test@example.com', password='test123')
        
        # Create test question
        self.question = Question.objects.create(
            title="Test Question",
            question="Test Question Content",
            mode=Question.ModeChoices.PENGAWASAN,
            id=uuid.uuid4(),
            user=self.user,
        )
        self.client.force_authenticate(user=self.user)
        self.question.tags.add(self.tag1, self.tag2)
        self.url = f'/question/{self.question.id}/'

    def test_get_question_not_found(self):
        """Test retrieval of non-existent question"""
        non_existent_id = uuid.uuid4()
        response = self.client.get(f'/api/questions/{non_existent_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    

    def test_get_question_unexpected_error(self):
        """Test unexpected error during question retrieval"""
        with patch('question.services.QuestionService.get') as mock_get:
            mock_get.side_effect = Exception('Unexpected error')
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    def test_get_question_success(self):
        """Test successful retrieval of a question"""
        response = self.client.get(f'/question/{self.question.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.question.id))
        self.assertEqual(response.data['title'], self.question.title)
        self.assertEqual(response.data['question'], self.question.question)
        self.assertEqual(response.data['mode'], self.question.mode)
        self.assertEqual(set(response.data['tags']), {'test_tag1', 'test_tag2'})
    
class TestQuestionGetRecentAnalysis(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/question/recent/'
        self.user = CustomUser.objects.create_user(username="testuser", email="testuser@example.com", password="password")
        self.client.force_authenticate(user=self.user)

        self.old_question = Question.objects.create(
            title="Old Question",
            question="Old Question Content",
            mode=Question.ModeChoices.PRIBADI,
            created_at=datetime(2024, 1, 1),
            id=uuid.uuid4()
        )

        self.recent_question = Question.objects.create(
            title="Recent Question",
            question="Recent Question Content",
            mode=Question.ModeChoices.PRIBADI,
            created_at=datetime(2025, 3, 1),
            id=uuid.uuid4()
        )

    def test_get_recent_analysis_success(self):
        """Test successful retrieval of the most recent question"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.recent_question.id))
        self.assertEqual(response.data['title'], self.recent_question.title)
        self.assertEqual(response.data['question'], self.recent_question.question)

    def test_get_recent_analysis_no_questions(self):
        """Test retrieval when no questions exist"""
        Question.objects.all().delete()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "No recent questions found.")   
    
    def test_get_recent_analysis_unexpected_error(self):
        """Test unexpected error during recent analysis retrieval"""
        with patch('question.services.QuestionService.get_recent') as mock_get_recent:
            # Paksa service untuk melempar exception
            mock_get_recent.side_effect = Exception("Unexpected error occurred")

            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.data['detail'], "Unexpected error occurred")
            
class QuestionResponseGetTagsTest(TestCase):
    def test_get_tags_without_all_method(self):
        # Arrange: obj.tags is a plain list, no .all()
        fake_question = SimpleNamespace(
            id=uuid.uuid4(),
            title='No all() tags',
            question='Plain tags',
            created_at=datetime.now(),
            mode='PRIBADI',
            tags=['tag1', 'tag2'],
            user=None
        )

        # Act
        serializer = QuestionResponse(instance=fake_question)
        data = serializer.data

        # Assert: fallback return path triggered
        self.assertEqual(data['tags'], ['tag1', 'tag2'])
