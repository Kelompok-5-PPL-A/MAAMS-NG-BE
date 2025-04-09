from tag.models import Tag
from validator.exceptions import UniqueTagException
from validator.constants import ErrorMsg
import pytest
from unittest.mock import Mock, patch
from question.models import Question 
from question.services import QuestionService
from django.test import TestCase
import uuid
from django.core.exceptions import ObjectDoesNotExist
from validator.exceptions import NotFoundRequestException
from authentication.models import CustomUser

class TestQuestionService():

    @pytest.fixture
    def question_service():
        return QuestionService()

    @pytest.fixture
    def mock_tag():
        return Mock(spec=Tag)

    def test_create_question_with_valid_data(question_service):
        # Arrange
        title = "Test Title"
        question = "Test Question"
        mode = Question.ModeChoices.PRIBADI
        tags = ["tag1", "tag2"]
        user = CustomUser.objects.create(username="testuser", password="password12389", email='testuser958@gmail.com')
        user.save()

        with patch('models.Question.objects.create') as mock_create:
            with patch.object(question_service, '_validate_tags') as mock_validate:
                mock_question = Mock()
                mock_create.return_value = mock_question
                mock_validate.return_value = [Mock(spec=Tag), Mock(spec=Tag)]
                
                # Act
                result = question_service.create(title, question, mode, tags, user)
                
                # Assert
                mock_create.assert_called_once_with(
                    title=title,
                    question=question,
                    mode=mode,
                    user=user
                )
                assert result == mock_question

    def test_validate_tags_with_existing_tags(question_service, mock_tag):
        # Arrange
        tags = ["existing_tag"]
        
        with patch('tag.models.Tag.objects.get') as mock_get:
            mock_get.return_value = mock_tag
            
            # Act
            result = question_service._validate_tags(tags)
            
            # Assert
            assert len(result) == 1
            assert result[0] == mock_tag

    def test_validate_tags_with_new_tags(question_service, mock_tag):
        # Arrange
        tags = ["new_tag"]
        
        with patch('tag.models.Tag.objects.get') as mock_get:
            with patch('tag.models.Tag.objects.create') as mock_create:
                mock_get.side_effect = Tag.DoesNotExist()
                mock_create.return_value = mock_tag
                
                # Act
                result = question_service._validate_tags(tags)
                
                # Assert
                assert len(result) == 1
                mock_create.assert_called_once_with(name="new_tag")

    def test_validate_tags_with_duplicate_tags(question_service, mock_tag):
        # Arrange
        tags = ["tag1", "tag1"]
        
        with patch('tag.models.Tag.objects.get') as mock_get:
            mock_get.return_value = mock_tag
            
            # Act & Assert
            with pytest.raises(UniqueTagException) as exc:
                question_service._validate_tags(tags)
            assert str(exc.value) == ErrorMsg.TAG_MUST_BE_UNIQUE

    def test_create_question_with_empty_tags(question_service):
        # Arrange
        title = "Test Title"
        question = "Test Question"
        mode = Question.ModeChoices.PRIBADI
        tags = []
        
        with patch('models.Question.objects.create') as mock_create:
            mock_question = Mock()
            mock_create.return_value = mock_question
            
            # Act
            result = question_service.create(title, question, mode, tags)
            
            # Assert
            mock_create.assert_called_once()
            assert result == mock_question

class TestQuestionService(TestCase):
    def setUp(self):
        self.service = QuestionService()
        self.question_id = uuid.uuid4()
        user = CustomUser.objects.create(username="testuser68", password="password12389", email='testuser969@gmail.com')
        user.save()
        self.question = Question.objects.create(
            id=self.question_id,
            title="Test Title",
            question="Test Question",
            mode="Test Mode",
            user=user,
        )
        self.tag = Tag.objects.create(name="test_tag")
        self.question.tags.add(self.tag)

    def test_get_question_not_found(self):
        # Test getting a question with non-existent ID
        with self.assertRaises(NotFoundRequestException) as context:
            self.service.get(uuid.uuid4())
        self.assertEqual(str(context.exception), ErrorMsg.NOT_FOUND)

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

    def test_validate_tags_duplicate_tag(self):
        # Test _validate_tags with duplicate tag
        tag_name = "duplicate"
        Tag.objects.create(name=tag_name)
        
        with self.assertRaises(UniqueTagException) as context:
            self.service._validate_tags([tag_name, tag_name])
        self.assertEqual(str(context.exception), ErrorMsg.TAG_MUST_BE_UNIQUE)