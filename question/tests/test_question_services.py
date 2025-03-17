from tag.models import Tag
from validator.exceptions import UniqueTagException
from validator.constants import ErrorMsg
import pytest
from unittest.mock import Mock, patch
from question.models import Question 
from question.services import QuestionService

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
        
        with patch('models.Question.objects.create') as mock_create:
            with patch.object(question_service, '_validate_tags') as mock_validate:
                mock_question = Mock()
                mock_create.return_value = mock_question
                mock_validate.return_value = [Mock(spec=Tag), Mock(spec=Tag)]
                
                # Act
                result = question_service.create(title, question, mode, tags)
                
                # Assert
                mock_create.assert_called_once_with(
                    title=title,
                    question=question,
                    mode=mode
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