from django.test import TestCase
from unittest.mock import Mock, patch
import uuid

from validator.constants import ErrorMsg
from validator.exceptions import NotFoundRequestException
from django.core.exceptions import ObjectDoesNotExist
from cause.models import Causes
from cause.services import CausesService
from cause.dataclasses.create_cause import CreateCauseDataClass
from question.models import Question

class TestCausesService(TestCase):
    def setUp(self):
        self.service = CausesService()
        self.valid_question_id = uuid.uuid4()
        self.valid_cause_data = {
            'cause': 'Test Cause',
            'row': 1,
            'column': 1,
            'mode': 'PRIBADI'
        }

    def test_create_cause_success(self):
        # Arrange
        mock_question = Mock(spec=Question)
        mock_question.id = self.valid_question_id

        mock_cause = Mock(spec=Causes)
        mock_cause.id = uuid.uuid4()
        mock_cause.question = mock_question
        mock_cause.row = self.valid_cause_data['row']
        mock_cause.column = self.valid_cause_data['column']
        mock_cause.mode = self.valid_cause_data['mode']
        mock_cause.cause = self.valid_cause_data['cause']
        mock_cause.status = False
        mock_cause.root_status = False
        mock_cause.feedback = ''

        with patch('question.models.Question.objects.get') as mock_get_question:
            with patch('cause.models.Causes.objects.create') as mock_create_cause:
                mock_get_question.return_value = mock_question
                mock_create_cause.return_value = mock_cause

                # Act
                result = self.service.create(
                    question_id=self.valid_question_id,
                    **self.valid_cause_data
                )

                # Assert
                self.assertIsInstance(result, CreateCauseDataClass)
                self.assertEqual(result.question_id, self.valid_question_id)
                self.assertEqual(result.cause, self.valid_cause_data['cause'])
                mock_get_question.assert_called_once_with(pk=self.valid_question_id)
                mock_create_cause.assert_called_once_with(
                    question=mock_question,
                    **self.valid_cause_data
                )

    def test_create_cause_question_not_found(self):
        # Arrange
        with patch('question.models.Question.objects.get') as mock_get_question:
            mock_get_question.side_effect = Question.DoesNotExist()

            # Act & Assert
            with self.assertRaises(Question.DoesNotExist):
                self.service.create(
                    question_id=self.valid_question_id,
                    **self.valid_cause_data
                )

    def test_create_cause_invalid_data(self):
        # Arrange
        invalid_data = {
            'cause': '',  # Empty cause
            'row': -1,    # Invalid row
            'column': -1, # Invalid column
            'mode': 'INVALID_MODE'
        }

        mock_question = Mock(spec=Question)
        mock_question.id = self.valid_question_id

        with patch('question.models.Question.objects.get') as mock_get_question:
            mock_get_question.return_value = mock_question
            with patch('cause.models.Causes.objects.create') as mock_create_cause:
                mock_create_cause.side_effect = ValueError()

                # Act & Assert
                with self.assertRaises(ValueError):
                    self.service.create(
                        question_id=self.valid_question_id,
                        **invalid_data
                    )

    def test_get_cause_success(self):
        # Arrange
        cause_id = uuid.uuid4()
        mock_cause = Mock(spec=Causes)
        mock_cause.id = cause_id
        mock_cause.question_id = self.valid_question_id
        mock_cause.row = 1
        mock_cause.column = 1
        mock_cause.mode = 'PRIBADI'
        mock_cause.cause = 'Test Cause'
        mock_cause.status = False
        mock_cause.root_status = False
        mock_cause.feedback = ''

        with patch('cause.models.Causes.objects.get') as mock_get_cause:
            mock_get_cause.return_value = mock_cause

            # Act
            result = self.service.get(
                question_id=self.valid_question_id,
                pk=cause_id
            )

            # Assert
            self.assertIsInstance(result, CreateCauseDataClass)
            self.assertEqual(result.question_id, self.valid_question_id)
            self.assertEqual(result.id, cause_id)
            mock_get_cause.assert_called_once_with(
                pk=cause_id, 
                question_id=self.valid_question_id
            )

    def test_get_cause_not_found(self):
        # Arrange
        cause_id = uuid.uuid4()
        with patch('cause.models.Causes.objects.get') as mock_get_cause:
            mock_get_cause.side_effect = ObjectDoesNotExist()

            # Act & Assert
            with self.assertRaises(NotFoundRequestException) as context:
                self.service.get(
                    question_id=self.valid_question_id,
                    pk=cause_id
                )
            
            self.assertEqual(str(context.exception), ErrorMsg.CAUSE_NOT_FOUND)

    def test_get_list_success(self):
        # Arrange
        cause_id1 = uuid.uuid4()
        cause_id2 = uuid.uuid4()
        
        mock_cause1 = Mock(spec=Causes)
        mock_cause1.id = cause_id1
        mock_cause1.question_id = self.valid_question_id
        mock_cause1.row = 1
        mock_cause1.column = 1
        mock_cause1.mode = 'PRIBADI'
        mock_cause1.cause = 'Test Cause 1'
        mock_cause1.status = False
        mock_cause1.root_status = False
        mock_cause1.feedback = ''

        mock_cause2 = Mock(spec=Causes)
        mock_cause2.id = cause_id2
        mock_cause2.question_id = self.valid_question_id
        mock_cause2.row = 2
        mock_cause2.column = 2
        mock_cause2.mode = 'PRIBADI'
        mock_cause2.cause = 'Test Cause 2'
        mock_cause2.status = False
        mock_cause2.root_status = False
        mock_cause2.feedback = ''

        mock_causes = [mock_cause1, mock_cause2]
        mock_question = Mock(spec=Question)

        with patch('cause.models.Causes.objects.filter') as mock_filter_causes:
            with patch('question.models.Question.objects.get') as mock_get_question:
                mock_filter_causes.return_value = mock_causes
                mock_get_question.return_value = mock_question

                # Act
                results = self.service.get_list(question_id=self.valid_question_id)

                # Assert
                self.assertEqual(len(results), 2)
                self.assertIsInstance(results[0], CreateCauseDataClass)
                self.assertIsInstance(results[1], CreateCauseDataClass)
                self.assertEqual(results[0].id, cause_id1)
                self.assertEqual(results[1].id, cause_id2)
                mock_filter_causes.assert_called_once_with(question_id=self.valid_question_id)
                mock_get_question.assert_called_once_with(pk=self.valid_question_id)

    def test_get_list_not_found(self):
        # Arrange
        with patch('cause.models.Causes.objects.filter') as mock_filter_causes:
            with patch('question.models.Question.objects.get') as mock_get_question:
                mock_get_question.side_effect = ObjectDoesNotExist()

                # Act & Assert
                with self.assertRaises(NotFoundRequestException) as context:
                    self.service.get_list(question_id=self.valid_question_id)
                
                self.assertEqual(str(context.exception), ErrorMsg.CAUSE_NOT_FOUND)

    def test_patch_cause_success(self):
        # Arrange
        cause_id = uuid.uuid4()
        new_cause_text = "Updated Cause Text"
        
        mock_cause = Mock(spec=Causes)
        mock_cause.id = cause_id
        mock_cause.question_id = self.valid_question_id
        mock_cause.row = 1
        mock_cause.column = 1
        mock_cause.mode = 'PRIBADI'
        mock_cause.cause = new_cause_text  # Updated text
        mock_cause.status = False
        mock_cause.root_status = False
        mock_cause.feedback = ''

        with patch('cause.models.Causes.objects.get') as mock_get_cause:
            mock_get_cause.return_value = mock_cause

            # Act
            result = self.service.patch_cause(
                question_id=self.valid_question_id,
                pk=cause_id,
                cause=new_cause_text
            )

            # Assert
            self.assertIsInstance(result, CreateCauseDataClass)
            self.assertEqual(result.cause, new_cause_text)
            mock_get_cause.assert_called_once_with(
                question_id=self.valid_question_id,
                pk=cause_id
            )
            self.assertTrue(mock_cause.save.called)

    def test_patch_cause_not_found(self):
        # Arrange
        cause_id = uuid.uuid4()
        new_cause_text = "Updated Cause Text"
        
        with patch('cause.models.Causes.objects.get') as mock_get_cause:
            mock_get_cause.side_effect = ObjectDoesNotExist()

            # Act & Assert
            with self.assertRaises(NotFoundRequestException) as context:
                self.service.patch_cause(
                    question_id=self.valid_question_id,
                    pk=cause_id,
                    cause=new_cause_text
                )
            
            self.assertEqual(str(context.exception), ErrorMsg.CAUSE_NOT_FOUND)

    def test_get_cause_object_does_not_exist(self):
        """Test get method when cause doesn't exist in database"""
        # Arrange
        with patch('cause.models.Causes.objects.get') as mock_get_cause:
            # Simulate Django's ObjectDoesNotExist exception
            mock_get_cause.side_effect = ObjectDoesNotExist()
            
            # Act & Assert
            with self.assertRaises(NotFoundRequestException) as context:
                self.service.get(
                    question_id=self.valid_question_id,
                    pk=self.valid_cause_id
                )
            
            # Verify the correct error message is included
            self.assertEqual(str(context.exception), ErrorMsg.CAUSE_NOT_FOUND)
            mock_get_cause.assert_called_once_with(
                pk=self.valid_cause_id, 
                question_id=self.valid_question_id
            )

    def test_get_list_question_does_not_exist(self):
        """Test get_list method when question doesn't exist"""
        # Arrange
        with patch('cause.models.Causes.objects.filter') as mock_filter_causes:
            mock_filter_causes.return_value = []
            with patch('question.models.Question.objects.get') as mock_get_question:
                # Simulate Django's ObjectDoesNotExist exception
                mock_get_question.side_effect = ObjectDoesNotExist()
                
                # Act & Assert
                with self.assertRaises(NotFoundRequestException) as context:
                    self.service.get_list(question_id=self.valid_question_id)
                
                # Verify the correct error message is included
                self.assertEqual(str(context.exception), ErrorMsg.CAUSE_NOT_FOUND)
                mock_get_question.assert_called_once_with(pk=self.valid_question_id)

    def test_get_list_causes_empty_but_no_error(self):
        """Test get_list method when causes are empty but question exists"""
        # Arrange
        mock_question = Mock(spec=Question)
        mock_question.id = self.valid_question_id
        
        # An empty list of causes
        mock_causes = []
        
        with patch('cause.models.Causes.objects.filter') as mock_filter_causes:
            with patch('question.models.Question.objects.get') as mock_get_question:
                mock_filter_causes.return_value = mock_causes
                mock_get_question.return_value = mock_question
                
                # Act
                results = self.service.get_list(question_id=self.valid_question_id)
                
                # Assert
                self.assertEqual(len(results), 0)  # Should be an empty list, not an error
                mock_filter_causes.assert_called_once_with(question_id=self.valid_question_id)
                mock_get_question.assert_called_once_with(pk=self.valid_question_id)

    def test_patch_cause_object_does_not_exist(self):
        """Test patch_cause method when cause doesn't exist"""
        # Arrange
        new_cause_text = "Updated Cause Text"
        
        with patch('cause.models.Causes.objects.get') as mock_get_cause:
            # Simulate Django's ObjectDoesNotExist exception
            mock_get_cause.side_effect = ObjectDoesNotExist()
            
            # Act & Assert
            with self.assertRaises(NotFoundRequestException) as context:
                self.service.patch_cause(
                    question_id=self.valid_question_id,
                    pk=self.valid_cause_id,
                    cause=new_cause_text
                )
            
            # Verify the correct error message is included
            self.assertEqual(str(context.exception), ErrorMsg.CAUSE_NOT_FOUND)
            mock_get_cause.assert_called_once_with(
                question_id=self.valid_question_id,
                pk=self.valid_cause_id
            )

    def test_create_question_does_not_exist(self):
        """Test create method when the referenced question doesn't exist"""
        # Arrange
        with patch('question.models.Question.objects.get') as mock_get_question:
            # Simulate Django's ObjectDoesNotExist exception
            mock_get_question.side_effect = ObjectDoesNotExist()
            
            # Act & Assert
            with self.assertRaises(ObjectDoesNotExist):
                self.service.create(
                    question_id=self.valid_question_id,
                    **self.valid_cause_data
                )
            
            mock_get_question.assert_called_once_with(pk=self.valid_question_id)