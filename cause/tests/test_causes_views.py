from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, Mock
import uuid
from cause.models import Causes
from cause.services import CausesService
from cause.dataclasses.create_cause import CreateCauseDataClass
from question.models import Question
from cause.serializers import CausesResponse
from validator.exceptions import NotFoundRequestException, ForbiddenRequestException

class TestCausesPostView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/cause/'
        self.valid_payload = {
            'question_id': str(uuid.uuid4()),
            'cause': 'Test Cause',
            'row': 1,
            'column': 1,
            'mode': 'PRIBADI'
        }
    
    @patch('cause.services.CausesService.create')
    def test_create_cause_success(self, mock_create):
        # Arrange
        mock_cause = CreateCauseDataClass(
            question_id=uuid.UUID(self.valid_payload['question_id']),
            id=uuid.uuid4(),
            row=self.valid_payload['row'],
            column=self.valid_payload['column'],
            mode=self.valid_payload['mode'],
            cause=self.valid_payload['cause'],
            status=False,
            root_status=False,
            feedback=''
        )
        mock_create.return_value = mock_cause

        # Act
        response = self.client.post(
            self.url,
            data=self.valid_payload,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_create.assert_called()
        call_args = mock_create.call_args[1]
        self.assertEqual(call_args['cause'], self.valid_payload['cause'])
        self.assertEqual(str(call_args['question_id']), self.valid_payload['question_id'])
        self.assertEqual(call_args['row'], self.valid_payload['row'])
        self.assertEqual(call_args['column'], self.valid_payload['column'])

    @patch('cause.services.CausesService.create')
    def test_create_cause_invalid_data(self, mock_create):
        # Arrange
        invalid_payload = {
            'question_id': str(uuid.uuid4()),
            'cause': '',  # Empty cause text
            'row': -1,    # Negative row value
            'column': -1, # Negative column value
            'mode': 'INVALID_MODE'
        }

        # Act
        response = self.client.post(
            self.url,
            data=invalid_payload,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_create.assert_not_called()
    
    @patch('cause.services.CausesService.create')
    def test_create_cause_question_not_found(self, mock_create):
        # Arrange - Negative case: Question doesn't exist
        mock_create.side_effect = NotFoundRequestException("Question not found")

        # Act
        response = self.client.post(
            self.url,
            data=self.valid_payload,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class TestCausesGetView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.question_id = str(uuid.uuid4())
        self.cause_id = str(uuid.uuid4())
        self.url_single = f'/cause/{self.question_id}/{self.cause_id}/'
        self.url_list = f'/cause/{self.question_id}/'
    
    @patch('cause.services.CausesService.get')
    def test_get_single_cause(self, mock_get):
        # Arrange
        mock_cause = CreateCauseDataClass(
            question_id=uuid.UUID(self.question_id),
            id=uuid.UUID(self.cause_id),
            row=1,
            column=1,
            mode='PRIBADI',
            cause='Test Cause',
            status=False,
            root_status=False,
            feedback=''
        )
        mock_get.return_value = mock_cause

        # Act
        response = self.client.get(self.url_single)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get.assert_called_once_with(
            self=CausesService,
            question_id=uuid.UUID(self.question_id),
            pk=uuid.UUID(self.cause_id)
        )
        # Verify key data fields are present
        self.assertEqual(response.data['id'], str(self.cause_id))
        self.assertEqual(response.data['question_id'], str(self.question_id))
        self.assertEqual(response.data['cause'], 'Test Cause')
    
    @patch('cause.services.CausesService.get_list')
    def test_get_cause_list(self, mock_get_list):
        # Arrange
        mock_cause1 = CreateCauseDataClass(
            question_id=uuid.UUID(self.question_id),
            id=uuid.uuid4(),
            row=1,
            column=1, 
            mode='PRIBADI',
            cause='Test Cause 1',
            status=False,
            root_status=False,
            feedback=''
        )
        
        mock_cause2 = CreateCauseDataClass(
            question_id=uuid.UUID(self.question_id),
            id=uuid.uuid4(),
            row=2,
            column=2,
            mode='PRIBADI',
            cause='Test Cause 2',
            status=False,
            root_status=False,
            feedback=''
        )
        
        mock_get_list.return_value = [mock_cause1, mock_cause2]
        
        # Act
        response = self.client.get(self.url_list)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        mock_get_list.assert_called_once_with(
            self=CausesService,
            question_id=uuid.UUID(self.question_id)
        )
        
    @patch('cause.services.CausesService.get')
    def test_get_cause_not_found(self, mock_get):
        # Arrange - Negative case
        mock_get.side_effect = NotFoundRequestException("Cause not found")

        # Act
        response = self.client.get(self.url_single)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    @patch('cause.services.CausesService.get_list')
    def test_get_empty_cause_list(self, mock_get_list):
        # Arrange - Corner case: Empty list
        mock_get_list.return_value = []

        # Act
        response = self.client.get(self.url_list)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    @patch('cause.services.CausesService.get')
    def test_get_cause_forbidden(self, mock_get):
        # Arrange - Negative case: Unauthorized access
        mock_get.side_effect = ForbiddenRequestException("Not authorized to view this cause")

        # Act
        response = self.client.get(self.url_single)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestCausesPatchView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.question_id = str(uuid.uuid4())
        self.cause_id = str(uuid.uuid4())
        self.url = f'/cause/patch/{self.question_id}/{self.cause_id}/'
        self.valid_payload = {
            'cause': 'Updated Cause'
        }
    
    @patch('cause.services.CausesService.patch_cause')
    def test_patch_cause_success(self, mock_patch_cause):
        # Arrange
        mock_cause = CreateCauseDataClass(
            question_id=uuid.UUID(self.question_id),
            id=uuid.UUID(self.cause_id),
            row=1,
            column=1,
            mode='PRIBADI',
            cause='Updated Cause',
            status=False,
            root_status=False,
            feedback=''
        )
        mock_patch_cause.return_value = mock_cause

        # Act
        response = self.client.patch(
            self.url,
            data=self.valid_payload,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_patch_cause.assert_called_once_with(
            self=CausesService,
            question_id=uuid.UUID(self.question_id),
            pk=uuid.UUID(self.cause_id),
            **self.valid_payload
        )
        # Verify key data is present
        self.assertEqual(response.data['cause'], 'Updated Cause')
        self.assertEqual(response.data['id'], str(self.cause_id))
    
    @patch('cause.services.CausesService.patch_cause')
    def test_patch_cause_invalid_data(self, mock_patch_cause):
        # Arrange
        invalid_payload = {
            'cause': ''  # Empty cause
        }

        # Act
        response = self.client.patch(
            self.url,
            data=invalid_payload,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_patch_cause.assert_not_called()
        
    @patch('cause.services.CausesService.patch_cause')
    def test_patch_cause_not_found(self, mock_patch_cause):
        # Arrange - Negative case
        mock_patch_cause.side_effect = NotFoundRequestException("Cause not found")

        # Act
        response = self.client.patch(
            self.url,
            data=self.valid_payload,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    @patch('cause.services.CausesService.patch_cause')
    def test_patch_cause_no_changes(self, mock_patch_cause):
        # Arrange - Corner case: No actual changes in payload
        empty_changes = {}
        
        # Act
        response = self.client.patch(
            self.url,
            data=empty_changes,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('cause.services.CausesService.patch_cause')
    def test_patch_cause_forbidden(self, mock_patch_cause):
        # Arrange - Negative case: Unauthorized update
        mock_patch_cause.side_effect = ForbiddenRequestException("Not authorized to update this cause")

        # Act
        response = self.client.patch(
            self.url,
            data=self.valid_payload,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)