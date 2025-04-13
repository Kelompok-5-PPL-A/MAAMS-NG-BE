from tag.models import Tag
from validator.exceptions import UniqueTagException, ForbiddenRequestException
from validator.constants import ErrorMsg
from django.test import TestCase
from unittest.mock import Mock, patch
from question.models import Question 
from question.services import QuestionService
import uuid
from django.core.exceptions import ObjectDoesNotExist
from validator.exceptions import NotFoundRequestException
from authentication.models import CustomUser

class TestQuestionService(TestCase):
    def setUp(self):
        self.service = QuestionService()
        self.question_id = uuid.uuid4()
        self.user = CustomUser.objects.create(username="testuser68", password="password12389", email='testuser969@gmail.com')
        self.user.save()
        self.question = Question.objects.create(
            id=self.question_id,
            title="Test Title",
            question="Test Question",
            mode="Test Mode",
            user=self.user,
        )
        self.tag = Tag.objects.create(name="test_tag")
        self.question.tags.add(self.tag)

    def test_create_question_with_valid_data(self):
        # Arrange
        title = "Test Title"
        question = "Test Question"
        mode = Question.ModeChoices.PRIBADI
        tags = ["tag1", "tag2"]
        user = self.user

        with patch('question.models.Question.objects.create') as mock_create:
            with patch.object(self.service, '_validate_tags') as mock_validate:
                mock_question = Mock()
                mock_create.return_value = mock_question
                mock_validate.return_value = [Mock(spec=Tag), Mock(spec=Tag)]
                
                # Act
                result = self.service.create(title, question, mode, tags, user)
                
                # Assert
                mock_create.assert_called_once_with(
                    title=title,
                    question=question,
                    mode=mode,
                    user=user
                )
                self.assertEqual(result, mock_question)

    def test_create_question_with_guest_user(self):
        # Arrange
        title = "Guest Title"
        question = "Guest Question"
        mode = Question.ModeChoices.PRIBADI
        tags = ["tag1", "tag2"]
        user = None  # Guest user

        with patch('question.models.Question.objects.create') as mock_create:
            with patch.object(self.service, '_validate_tags') as mock_validate:
                mock_question = Mock()
                mock_create.return_value = mock_question
                mock_validate.return_value = [Mock(spec=Tag), Mock(spec=Tag)]
                
                # Act
                result = self.service.create(title, question, mode, tags, user)
                
                # Assert
                mock_create.assert_called_once_with(
                    title=title,
                    question=question,
                    mode=mode,
                    user=None
                )
                self.assertEqual(result, mock_question)

    def test_get_question_not_found(self):
        # Test getting a question with non-existent ID
        with self.assertRaises(NotFoundRequestException) as context:
            self.service.get(uuid.uuid4())
        self.assertEqual(str(context.exception), ErrorMsg.NOT_FOUND)

    def test_get_recent_with_authenticated_user(self):
        # Test get_recent with authenticated user
        with patch('question.models.Question.objects.filter') as mock_filter:
            mock_query = Mock()
            mock_filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.first.return_value = self.question

            # Act
            result = self.service.get_recent(self.user)
            
            # Assert
            mock_filter.assert_called_once_with(user=self.user)
            mock_query.order_by.assert_called_once_with('-created_at')
            self.assertEqual(result, self.question)

    def test_get_recent_with_guest_user(self):
        # Test get_recent with guest user (should return None)
        result = self.service.get_recent(user=None)
        self.assertIsNone(result)

    def test_get_recent_no_questions(self):
        # Test get_recent when user has no questions
        user_without_questions = CustomUser.objects.create(
            username="no_questions", 
            password="password12389", 
            email='no_questions@gmail.com'
        )
        
        with self.assertRaises(Question.DoesNotExist) as context:
            self.service.get_recent(user_without_questions)
        self.assertEqual(str(context.exception), "No recent questions found.")

    def test_make_question_response_empty_list(self):
        # Test _make_question_response with empty list
        response = self.service._make_question_response([])
        self.assertEqual(response, [])
    
    def test_make_question_response_with_question(self):
        # Test _make_question_response with a question object
        response = self.service._make_question_response([self.question])
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0].id, self.question.id)
        self.assertEqual(response[0].title, self.question.title)
        self.assertEqual(response[0].question, self.question.question)
        self.assertEqual(response[0].mode, self.question.mode)
        self.assertEqual(response[0].username, self.user.username)  # Check username field

    def test_make_question_response_with_guest_question(self):
        # Test _make_question_response with a question created by guest
        guest_question = Question.objects.create(
            id=uuid.uuid4(),
            title="Guest Title",
            question="Guest Question",
            mode="Test Mode",
            user=None,  # Guest user
        )
        guest_question.tags.add(self.tag)
        
        response = self.service._make_question_response([guest_question])
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0].id, guest_question.id)
        self.assertEqual(response[0].title, guest_question.title)
        self.assertEqual(response[0].question, guest_question.question)
        self.assertEqual(response[0].mode, guest_question.mode)
        self.assertIsNone(response[0].username)  # Username should be None for guest

    def test_validate_tags_with_existing_tags(self):
        # Arrange
        tags = ["existing_tag"]
        
        with patch('tag.models.Tag.objects.get') as mock_get:
            mock_tag = Mock(spec=Tag)
            mock_get.return_value = mock_tag
            
            # Act
            result = self.service._validate_tags(tags)
            
            # Assert
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], mock_tag)

    def test_validate_tags_with_new_tags(self):
        # Arrange
        tags = ["new_tag"]
        
        with patch('tag.models.Tag.objects.get') as mock_get:
            with patch('tag.models.Tag.objects.create') as mock_create:
                mock_tag = Mock(spec=Tag)
                mock_get.side_effect = Tag.DoesNotExist()
                mock_create.return_value = mock_tag
                
                # Act
                result = self.service._validate_tags(tags)
                
                # Assert
                self.assertEqual(len(result), 1)
                mock_create.assert_called_once_with(name="new_tag")

    def test_validate_tags_with_duplicate_tags(self):
        # Arrange
        tags = ["tag1", "tag1"]
        
        with patch('tag.models.Tag.objects.get') as mock_get:
            mock_tag = Mock(spec=Tag)
            mock_get.return_value = mock_tag
            
            # Act & Assert
            with self.assertRaises(UniqueTagException) as context:
                self.service._validate_tags(tags)
            self.assertEqual(str(context.exception), ErrorMsg.TAG_MUST_BE_UNIQUE)

    def test_validate_tags_duplicate_tag(self):
        # Test _validate_tags with duplicate tag
        tag_name = "duplicate"
        Tag.objects.create(name=tag_name)
        
        with self.assertRaises(UniqueTagException) as context:
            self.service._validate_tags([tag_name, tag_name])
        self.assertEqual(str(context.exception), ErrorMsg.TAG_MUST_BE_UNIQUE)

    def test_get_privileged_with_admin_and_valid_filter(self):
        # Arrange
        admin_user = CustomUser.objects.create(
            username="admin", 
            password="password123", 
            email="admin@example.com",
            is_superuser=True, 
            is_staff=True
        )
        question_pengawasan = Question.objects.create(
            id=uuid.uuid4(),
            title="Pengawasan Question",
            question="Should be visible to admin",
            mode=Question.ModeChoices.PENGAWASAN,
            user=admin_user,
        )
        
        # Act
        result = self.service.get_privileged("semua", admin_user, "")

        # Assert
        self.assertIn(question_pengawasan, result)

    def test_get_privileged_forbidden_for_non_admin(self):
        # Arrange
        non_admin = CustomUser.objects.create(
            username="user", 
            password="password123", 
            email="user@example.com",
            is_superuser=False, 
            is_staff=False
        )

        # Act & Assert
        with self.assertRaises(ForbiddenRequestException) as context:
            self.service.get_privileged("semua", non_admin, "keyword")
        self.assertEqual(str(context.exception), ErrorMsg.FORBIDDEN_GET)

    # ini test buat filter
    def test_get_privileged_returns_filtered_results(self):
        # Arrange
        admin_user = CustomUser.objects.create(
            username="admin", 
            password="password123", 
            email="admin@example.com",
            is_superuser=True, 
            is_staff=True
        )
        matching_question = Question.objects.create(
            id=uuid.uuid4(),
            title="Filter Match",
            question="This contains keyword",
            mode=Question.ModeChoices.PENGAWASAN,
            user=admin_user,
        )
        non_matching_question = Question.objects.create(
            id=uuid.uuid4(),
            title="No Match",
            question="Irrelevant",
            mode=Question.ModeChoices.PENGAWASAN,
            user=admin_user,
        )

        # Simulasi filter 'judul' dengan keyword "Match"
        with patch.object(self.service, '_resolve_filter_type') as mock_resolve:
            mock_resolve.return_value = Q(title__icontains="Match")

            # Act
            result = self.service.get_privileged("judul", admin_user, "Match")

        # Assert
        self.assertIn(matching_question, result)
        self.assertNotIn(non_matching_question, result)


    