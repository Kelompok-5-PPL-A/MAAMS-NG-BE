from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, Mock, ANY
from question.dataclasses.field_values import FieldValuesDataClass
from question.models import Question
from question.serializers import QuestionResponse
from tag.models import Tag
from datetime import datetime
import uuid
from authentication.models import CustomUser
from types import SimpleNamespace
from django.utils import timezone

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

    def test_create_question_as_authenticated_user(self):
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
            self.assertEqual(response.data['username'], self.user.username)  # Check username field
            mock_create.assert_called_once_with(
                title='Test Titles',
                question='Test Question',
                mode=Question.ModeChoices.PRIBADI,
                user=self.user,
                tags=['tag1', 'tag2']
            )

    def test_create_question_as_guest_user(self):
        # Arrange - no authentication
        mock_question = Mock(spec=Question)
        mock_question.id = '123e4567-e89b-12d3-a456-426614174001'
        mock_question.title = self.valid_payload['title']
        mock_question.question = self.valid_payload['question']
        mock_question.mode = self.valid_payload['mode']
        mock_question.created_at = datetime.now().isoformat() + 'Z'
        mock_question.tags.all.return_value = [
            Tag(name=tag) for tag in self.valid_payload['tags']
        ]
        mock_question.user = None  # Guest user has no user object

        with patch('question.services.QuestionService.create') as mock_create:
            mock_create.return_value = mock_question
            
            # Act - not authenticating the client
            response = self.client.post(
                self.url,
                data=self.valid_payload,
                format='json'
            )

            # Assert
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['title'], self.valid_payload['title'])
            self.assertIsNone(response.data['username'])  # Username should be None for guest
            self.assertIsNone(response.data['user'])      # User should be None for guest
            mock_create.assert_called_once_with(
                title='Test Titles',
                question='Test Question',
                mode=Question.ModeChoices.PRIBADI,
                user=None,  # Should pass None as user
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
        self.assertEqual(response.data['username'], self.user.username)


class TestQuestionGetRecentAnalysis(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/question/recent/'
        self.user = CustomUser.objects.create_user(username="testuser", email="testuser@example.com", password="password")
        self.client.force_authenticate(user=self.user)

        # Create questions for the user
        self.old_question = Question.objects.create(
            title="Old Question",
            question="Old Question Content",
            mode=Question.ModeChoices.PRIBADI,
            created_at=timezone.make_aware(datetime(2024, 1, 1)),
            id=uuid.uuid4(),
            user=self.user
        )

        self.recent_question = Question.objects.create(
            title="Recent Question",
            question="Recent Question Content",
            mode=Question.ModeChoices.PRIBADI,
            created_at=timezone.make_aware(datetime(2025, 3, 1)),
            id=uuid.uuid4(),
            user=self.user
        )

    def test_get_recent_analysis_success(self):
        """Test successful retrieval of the most recent question"""
        with patch('question.services.QuestionService.get_recent') as mock_get_recent:
            mock_get_recent.return_value = self.recent_question
            
            response = self.client.get(self.url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['id'], str(self.recent_question.id))
            self.assertEqual(response.data['title'], self.recent_question.title)
            self.assertEqual(response.data['question'], self.recent_question.question)
            self.assertEqual(response.data['username'], self.user.username)  # Check username
            
            # Verify the correct user was passed
            mock_get_recent.assert_called_once_with(ANY, user=self.user)

    def test_get_recent_analysis_no_questions(self):
        """Test retrieval when no questions exist for the user"""
        with patch('question.services.QuestionService.get_recent') as mock_get_recent:
            mock_get_recent.side_effect = Question.DoesNotExist("No recent questions found.")
            
            response = self.client.get(self.url)

            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertEqual(response.data['detail'], "No recent questions found.")
    
    def test_get_recent_analysis_guest_user(self):
        """Test retrieval when user is not authenticated"""
        # Use a client without authentication
        guest_client = APIClient()
        
        response = guest_client.get(self.url)
        # Should return 401 since endpoint requires authentication
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_recent_analysis_unexpected_error(self):
        """Test unexpected error during recent analysis retrieval"""
        with patch('question.services.QuestionService.get_recent') as mock_get_recent:
            # Force service to throw exception
            mock_get_recent.side_effect = Exception("Unexpected error occurred")

            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.data['detail'], "Unexpected error occurred")
    
    def test_get_recent_analysis_returns_none(self):
        """Test when get_recent returns None (no exception), should return specific 404 message"""
        with patch('question.services.QuestionService.get_recent') as mock_get_recent:
            mock_get_recent.return_value = None  # <--- ini bikin masuk ke if not recent_question

            response = self.client.get(self.url)

            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

            

class QuestionResponseSerializerTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", email="test@example.com", password="password")
    
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
    
    def test_get_username_with_user(self):
        # Test serializer with authenticated user
        fake_question = SimpleNamespace(
            id=uuid.uuid4(),
            title='User question',
            question='With username',
            created_at=datetime.now(),
            mode='PRIBADI',
            tags=['tag1', 'tag2'],
            user=self.user
        )
        
        serializer = QuestionResponse(instance=fake_question)
        data = serializer.data
        
        self.assertEqual(data['username'], self.user.username)
    
    def test_get_username_with_guest(self):
        # Test serializer with guest user (None)
        fake_question = SimpleNamespace(
            id=uuid.uuid4(),
            title='Guest question',
            question='No username',
            created_at=datetime.now(),
            mode='PRIBADI',
            tags=['tag1', 'tag2'],
            user=None
        )
        
        serializer = QuestionResponse(instance=fake_question)
        data = serializer.data
        
        self.assertIsNone(data['username'])
        self.assertIsNone(data['user'])

class TestQuestionGetPrivileged(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/question/history/privileged/'
        self.user = CustomUser.objects.create_user(
            username="regularuser", email="user@example.com", password="password"
        )
        self.admin_user = CustomUser.objects.create_user(
            username="adminuser", email="admin@example.com", password="password"
        )
        self.admin_user.is_superuser = True
        self.admin_user.is_staff = True
        self.admin_user.save()

        self.question1 = Question.objects.create(
            id=uuid.uuid4(),
            title="Privileged Q1",
            question="Isi Q1",
            mode=Question.ModeChoices.PENGAWASAN,
            created_at=timezone.now(),
            user=self.admin_user
        )

    def test_get_privileged_success_as_superuser(self):
        """Test superuser can successfully access get_privileged"""
        self.client.force_authenticate(user=self.admin_user)

        with patch('question.services.QuestionService.get_privileged') as mock_get:
            mock_get.return_value = [self.question1]

            response = self.client.get(self.url + '?filter=recent&keyword=test')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue("results" in response.data)
            self.assertEqual(len(response.data["results"]), 1)
            mock_get.assert_called_once_with(
                q_filter='recent',
                user=self.admin_user,
                keyword='test'
            )

    def test_get_privileged_authenticated_regular_user_forbidden(self):
        """Test that regular authenticated users are forbidden"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_get_privileged_unauthenticated_user_unauthorized(self):
        """Test unauthenticated (guest) user gets unauthorized"""
        guest_client = APIClient()
        response = guest_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_privileged_empty_result(self):
        """Test superuser receives empty result without error"""
        self.client.force_authenticate(user=self.admin_user)

        with patch('question.services.QuestionService.get_privileged') as mock_get:
            mock_get.return_value = []

            response = self.client.get(self.url + '?filter=recent')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["results"], [])

    def test_get_privileged_unexpected_error(self):
        """Test server error when something unexpected occurs"""
        self.client.force_authenticate(user=self.admin_user)

        with patch('question.services.QuestionService.get_privileged') as mock_get:
            mock_get.side_effect = Exception("Unexpected failure")

            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn("detail", response.data)
            self.assertIn("Unexpected failure", response.data["detail"])


    # Test filter admin
    def test_get_privileged_filter_semua_returns_all_pengawasan(self):
        """Test superuser gets all PENGAWASAN questions when using 'semua' filter"""
        self.client.force_authenticate(user=self.admin_user)

        with patch('question.services.QuestionService.get_privileged') as mock_get:
            mock_get.return_value = [self.question1]

            response = self.client.get(self.url + '?filter=semua')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["results"]), 1)
            mock_get.assert_called_once_with(
                q_filter='semua',
                user=self.admin_user,
                keyword=''
            )
    
    def test_get_privileged_invalid_filter_returns_server_error(self):
        """Test unknown filter value returns server error"""
        self.client.force_authenticate(user=self.admin_user)

        with patch('question.services.QuestionService.get_privileged') as mock_get:
            mock_get.side_effect = ValueError("Invalid filter value")

            response = self.client.get(self.url + '?filter=unknown_filter')

            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn("detail", response.data)
            self.assertIn("Invalid filter value", response.data["detail"])

    def test_get_privileged_missing_filter_still_works_with_default(self):
        """Test when filter is missing, still handles it gracefully"""
        self.client.force_authenticate(user=self.admin_user)

        with patch('question.services.QuestionService.get_privileged') as mock_get:
            mock_get.return_value = [self.question1]

            response = self.client.get(self.url + '?keyword=Privileged')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            mock_get.assert_called_once_with(
                q_filter=None,
                user=self.admin_user,
                keyword='Privileged'
            )

    def test_get_privileged_with_filter_but_empty_keyword(self):
        """Test filter applied but keyword is empty string"""
        self.client.force_authenticate(user=self.admin_user)

        with patch('question.services.QuestionService.get_privileged') as mock_get:
            mock_get.return_value = []

            response = self.client.get(self.url + '?filter=judul&keyword=')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            mock_get.assert_called_once_with(
                q_filter='judul',
                user=self.admin_user,
                keyword=''
            )

class QuestionDeleteTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='owner', email='owner@example.com', password='password123')
        self.other_user = CustomUser.objects.create_user(username='other_user', email='other@example.com', password='password456')
        self.question = Question.objects.create(
            id=uuid.uuid4(),
            question="Test question",
            user=self.user
        )
        self.guest_question = Question.objects.create(
            id=uuid.uuid4(),
            question="Guest question",
            user=None  # Indicates the question was created by a guest
        )
        self.url = f"/question/{self.question.id}/delete/"
        self.guest_url = f"/question/{self.guest_question.id}/delete/"

    def test_delete_question_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Question.objects.filter(id=self.question.id).exists())

    def test_delete_question_not_found(self):
        self.client.force_authenticate(user=self.user)
        non_existent_id = uuid.uuid4()
        response = self.client.delete(f"/question/{non_existent_id}/delete/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Analisis tidak ditemukan")

    def test_delete_question_unauthorized(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Question.objects.filter(id=self.question.id).exists())

    def test_guest_delete_question_success(self):
        response = self.client.delete(self.guest_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Question.objects.filter(id=self.guest_question.id).exists())

    def test_guest_delete_question_not_found(self):
        non_existent_id = uuid.uuid4()
        response = self.client.delete(f"/question/{non_existent_id}/delete/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Analisis tidak ditemukan")

    def test_delete_question_unexpected_error(self):
        with patch('question.services.QuestionService.get', side_effect=Exception("Unexpected error")):
            self.client.force_authenticate(user=self.user)
            response = self.client.delete(self.url)
            
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            self.assertIn("An unexpected error occurred", response.data['detail'])
            self.assertIn("Unexpected error", response.data['detail'])

            
class TestQuestionServiceErrors(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("get_matched")
        self.user = CustomUser.objects.create_user(
            email="admin@example.com",
            password="password123",
        )

    def test_get_matched_internal_server_error(self):
        """Test internal server error handling in get_matched view"""
        self.client.force_authenticate(user=self.user)
        # Patch the service method to raise an unexpected Exception
        with patch('question.services.QuestionService.get_matched') as mock_get:
            mock_get.side_effect = Exception("Unexpected error")

            response = self.client.get(self.url, {
                'filter': 'semua',
                'time_range': 'last_week',
                'keyword': 'anything'
            })

            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn("detail", response.data)
            self.assertIn("Unexpected error", response.data["detail"])
        
    def test_get_matched(self):
        """Test get_matched view with valid parameters"""
        self.client.force_authenticate(user=self.user)

        # Create a question for the user
        question = Question.objects.create(
            title="Test Title",
            question="Test Question",
            mode=Question.ModeChoices.PRIBADI,
            created_at=timezone.now(),
            id=uuid.uuid4(),
            user=self.user
        )
        question.tags.add(Tag.objects.create(name="tag1"))

        with patch('question.services.QuestionService.get_matched') as mock_get:
            mock_get.return_value = [question]

            response = self.client.get(self.url, {
                'filter': 'semua',
                'time_range': 'last_week',
                'keyword': 'anything'
            })

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['results']), 1)
            self.assertEqual(response.data['results'][0]['title'], question.title)
            self.assertEqual(response.data['results'][0]['question'], question.question)

class TestQuestionGetAll(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/question/history/'
        self.user = CustomUser.objects.create_user(
            username="testuser", email="testuser@example.com", password="password123"
        )
    
        self.client.force_authenticate(user=self.user)
    
    def test_internal_server_error(self):
        """Test internal server error during get_all"""
        with patch('question.services.QuestionService.get_all') as mock_get:
            mock_get.side_effect = Exception("Internal server error")
            
            response = self.client.get(self.url)
            
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn("detail", response.data)
            self.assertIn("Internal server error", response.data["detail"])
    
    def test_no_history_found(self):
        """Test no history found for the user"""
        with patch('question.services.QuestionService.get_all') as mock_get:
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(list(response.data['results']), [])

    def test_get_all_success(self):
        """Test successful retrieval of all questions"""
        question1 = Question.objects.create(
            title="Question 1",
            question="Content 1",
            mode=Question.ModeChoices.PRIBADI,
            created_at=timezone.now(),
            id=uuid.uuid4(),
            user=self.user
        )
        question2 = Question.objects.create(
            title="Question 2",
            question="Content 2",
            mode=Question.ModeChoices.PRIBADI,
            created_at=timezone.now(),
            id=uuid.uuid4(),
            user=self.user
        )

        with patch('question.services.QuestionService.get_all') as mock_get:
            mock_get.return_value = [question1, question2]
            
            response = self.client.get(self.url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['results']), 2)
            self.assertEqual(response.data['results'][0]['question'], question1.question)
            self.assertEqual(response.data['results'][1]['question'], question2.question)

class TestQuestionGetFieldValues(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/question/history/field-values/'
        self.user = CustomUser.objects.create_user(
            username="testuser", email="testuser@example.com", password="password123"
        )
        self.admin_user = CustomUser.objects.create_user(
            username="adminuser", email="adminuser@example.com", password="adminpassword123", is_superuser=True, is_staff=True
        )
        self.client.force_authenticate(user=self.user)
        self.client.force_authenticate(user=self.admin_user)

    def test_get_field_values_as__user(self):
        """Test field values retrieval for user"""
        question1 = Question.objects.create(
            title="Question 1",
            question="Content 1",
            mode=Question.ModeChoices.PRIBADI,
            user=self.user
        )
        question2 = Question.objects.create(
            title="Question 2",
            question="Content 2",
            mode=Question.ModeChoices.PENGAWASAN,
            user=self.user
        )
        tag1 = Tag.objects.create(name="Tag1")
        tag2 = Tag.objects.create(name="Tag2")
        question1.tags.add(tag1)
        question2.tags.add(tag2)

        with patch('question.services.QuestionService.get_field_values') as mock_service:
            mock_service.return_value = FieldValuesDataClass(
                pengguna=[],
                judul=["Question 1", "Question 2"],
                topik=["Tag1", "Tag2"]
            )

            response = self.client.get(self.url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['judul'], ["Question 1", "Question 2"])
            self.assertEqual(response.data['topik'], ["Tag1", "Tag2"])
            self.assertEqual(response.data['pengguna'], [])

    def test_get_field_values_as_admin_user(self):
        """Test field values retrieval for an admin user"""

        with patch('question.services.QuestionService.get_field_values') as mock_service:
            mock_service.return_value = FieldValuesDataClass(
                pengguna=["testuser", "adminuser"],
                judul=["Admin Question"],
                topik=["Admin Tag"]
            )

            response = self.client.get(self.url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['judul'], ["Admin Question"])
            self.assertEqual(response.data['topik'], ["Admin Tag"])
            self.assertEqual(response.data['pengguna'], ["testuser", "adminuser"])


class TestQuestionPatch(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='testuser', email='user@example.com', password='pass123')
        self.client.force_authenticate(user=self.user)

        self.question = Question.objects.create(
            id=uuid.uuid4(),
            title="Old Title",
            question="Old Content",
            mode=Question.ModeChoices.PRIBADI,
            user=self.user
        )
        self.tag1 = Tag.objects.create(name="Tag1")
        self.tag2 = Tag.objects.create(name="Tag2")
        self.question.tags.set([self.tag1, self.tag2])

        self.mode_url = f'/question/ubah/{self.question.id}/'
        self.title_url = f'/question/ubah/judul/{self.question.id}/'
        self.tags_url = f'/question/ubah/tags/{self.question.id}/'

    def test_patch_mode_success(self):
        """Positive: Successfully update mode"""
        with patch('question.services.QuestionService.update_question') as mock_update:
            mock_question = self.question
            mock_question.mode = Question.ModeChoices.PENGAWASAN
            mock_update.return_value = mock_question

            response = self.client.patch(self.mode_url, data={'mode': 'PENGAWASAN'}, format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['mode'], 'PENGAWASAN')

    def test_patch_title_success(self):
        """Positive: Successfully update title"""
        with patch('question.services.QuestionService.update_question') as mock_update:
            mock_question = self.question
            mock_question.title = "New Title"
            mock_update.return_value = mock_question

            response = self.client.patch(self.title_url, data={'title': 'New Title'}, format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['title'], 'New Title')

    def test_patch_tags_success(self):
        """Positive: Successfully update tags"""
        with patch('question.services.QuestionService.update_question') as mock_update:
            mock_question = self.question
            mock_question.tags.all.return_value = [self.tag1, self.tag2]
            mock_update.return_value = mock_question

            response = self.client.patch(self.tags_url, data={'tags': ['Tag1', 'Tag2']}, format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['tags']), 2)

    def test_patch_tags_full_flow(self):
        """Positive: Patch tags with full flow to cover serializer and update"""
        # Buat tag baru yang akan dikirim lewat request
        new_tag = Tag.objects.create(name="Tag3")

        response = self.client.patch(self.tags_url, data={'tags': ['Tag3']}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tags', response.data)
        self.assertEqual(response.data['tags'][0]['name'], 'Tag3')


    def test_patch_mode_invalid_payload(self):
        """Negative: Invalid mode data"""
        response = self.client.patch(self.mode_url, data={'mode': 'INVALID'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_title_missing_field(self):
        """Negative: Missing title field"""
        response = self.client.patch(self.title_url, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_tags_empty_list(self):
        """Edge: Empty tag list is accepted (assume valid unless restricted)"""
        with patch('question.services.QuestionService.update_question') as mock_update:
            mock_question = self.question
            mock_question.tags.all.return_value = []
            mock_update.return_value = mock_question

            response = self.client.patch(self.tags_url, data={'tags': []}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['tags'], [])

    def test_patch_unauthenticated(self):
        """Negative: Cannot patch if unauthenticated"""
        self.client.force_authenticate(user=None)
        response = self.client.patch(self.mode_url, data={'mode': 'PENGAWASAN'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)