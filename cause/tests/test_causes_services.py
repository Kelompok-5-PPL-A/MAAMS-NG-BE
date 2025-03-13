from django.test import TestCase
from unittest.mock import Mock, patch
import uuid
from ..models import Causes
from ..services import CausesService
from ..dataclasses.create_cause import CreateCauseDataClass
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