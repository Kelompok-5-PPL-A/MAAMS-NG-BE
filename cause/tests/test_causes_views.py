from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, Mock
import uuid
from cause.models import Causes
from cause.services import CausesService
from cause.dataclasses.create_cause import CreateCauseDataClass
from question.models import Question
from validator.exceptions import NotFoundRequestException, ForbiddenRequestException

class TestCausesPostView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/causes/submit/'
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
        mock_cause = Mock()
        mock_cause.id = uuid.uuid4()
        mock_cause.question_id = self.valid_payload['question_id']
        mock_cause.cause = self.valid_payload['cause']
        mock_cause.row = self.valid_payload['row']
        mock_cause.column = self.valid_payload['column']
        mock_cause.mode = self.valid_payload['mode']
        mock_create.return_value = mock_cause

        # Act
        response = self.client.post(
            self.url,
            data=self.valid_payload,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_create.assert_called_once_with(
            **self.valid_payload
        )

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
    def test_create_cause_with_long_text(self, mock_create):
        # Arrange - Corner case: Very long cause text
        long_payload = self.valid_payload.copy()
        long_payload['cause'] = 'A' * 1000  # Very long text
        
        mock_cause = Mock()
        mock_create.return_value = mock_cause

        # Act
        response = self.client.post(
            self.url,
            data=long_payload,
            format='json'
        )

        # Assert - Should handle long text appropriately
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    @patch('cause.services.CausesService.create')
    def test_create_cause_with_special_characters(self, mock_create):
        # Arrange - Corner case: Special characters
        special_payload = self.valid_payload.copy()
        special_payload['cause'] = "Test's with \"special\" characters & symbols !@#$%^"
        
        mock_cause = Mock()
        mock_create.return_value = mock_cause

        # Act
        response = self.client.post(
            self.url,
            data=special_payload,
            format='json'
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
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

    @patch('cause.serializers.CausesRequest.is_valid')
    def test_create_cause_validation_error(self, mock_is_valid):
        # Arrange
        mock_is_valid.side_effect = Exception("Validation error")
        
        # Act
        response = self.client.post(
            self.url,
            data={'invalid': 'data'},
            format='json'
        )
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('cause.services.CausesService.create')
    @patch('cause.serializers.CausesResponse.__init__')
    def test_create_cause_response_serialization(self, mock_response_serializer, mock_create):
        # Arrange
        mock_cause = Mock()
        mock_create.return_value = mock_cause
        mock_response_serializer.return_value = None  # Constructor returns None
        
        # Act
        response = self.client.post(
            self.url,
            data=self.valid_payload,
            format='json'
        )
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_response_serializer.assert_called_once_with(mock_cause)
    
    @patch('cause.services.CausesService.create')
    def test_create_cause_server_error(self, mock_create):
        # Arrange
        mock_create.side_effect = Exception("Unexpected server error")
        
        # Act
        response = self.client.post(
            self.url,
            data=self.valid_payload,
            format='json'
        )
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('cause.serializers.CausesRequest')
    @patch('cause.services.CausesService.create')
    @patch('cause.serializers.CausesResponse')
    def test_post_method_full_flow(self, mock_response_serializer, mock_create, mock_request_serializer):
        # Arrange
        mock_request_instance = Mock()
        mock_request_serializer.return_value = mock_request_instance
        mock_request_instance.is_valid.return_value = True
        mock_request_instance.validated_data = self.valid_payload
        
        mock_cause = Mock()
        mock_create.return_value = mock_cause
        
        mock_response_instance = Mock()
        mock_response_serializer.return_value = mock_response_instance
        mock_response_instance.data = {"id": "123", "cause": "Test Cause"}

        # Act
        response = self.client.post(
            self.url,
            data=self.valid_payload,
            format='json'
        )
        
        # Assert
        mock_request_serializer.assert_called_once()
        mock_request_instance.is_valid.assert_called_once_with(raise_exception=True)
        mock_create.assert_called_once()
        mock_response_serializer.assert_called_once_with(mock_cause)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, mock_response_instance.data)

class TestCausesGetView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.question_id = str(uuid.uuid4())
        self.cause_id = str(uuid.uuid4())
        self.url_single = f'/causes/{self.question_id}/{self.cause_id}/'
        self.url_list = f'/causes/{self.question_id}/'
    
    @patch('cause.services.CausesService.get')
    def test_get_single_cause(self, mock_get):
        # Arrange
        mock_cause = Mock()
        mock_get.return_value = mock_cause

        # Act
        response = self.client.get(self.url_single)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get.assert_called_once_with(
            question_id=self.question_id,
            pk=self.cause_id
        )
    
    @patch('cause.services.CausesService.get_list')
    def test_get_cause_list(self, mock_get_list):
        # Arrange
        mock_causes = [Mock(), Mock()]
        mock_get_list.return_value = mock_causes

        # Act
        response = self.client.get(self.url_list)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_list.assert_called_once_with(
            question_id=self.question_id
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
    
    def test_get_cause_with_invalid_uuid(self):
        # Arrange - Negative case: Invalid UUID
        url_invalid = f'/causes/{self.question_id}/not-a-uuid/'

        # Act
        response = self.client.get(url_invalid)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    @patch('cause.services.CausesService.get')
    @patch('cause.serializers.CausesResponse.__init__')
    def test_get_cause_response_serialization(self, mock_response_serializer, mock_get):
        # Arrange
        mock_cause = Mock()
        mock_get.return_value = mock_cause
        mock_response_serializer.return_value = None  # Constructor returns None
        
        # Act
        response = self.client.get(self.url_single)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_response_serializer.assert_called_once_with(mock_cause)
    
    @patch('cause.services.CausesService.get')
    def test_get_cause_server_error(self, mock_get):
        # Arrange
        mock_get.side_effect = Exception("Unexpected server error")
        
        # Act
        response = self.client.get(self.url_single)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestCausesPatchView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.question_id = str(uuid.uuid4())
        self.cause_id = str(uuid.uuid4())
        self.url = f'/causes/{self.question_id}/{self.cause_id}/'
        self.valid_payload = {
            'cause': 'Updated Cause'
        }
    
    @patch('cause.services.CausesService.patch_cause')
    def test_patch_cause_success(self, mock_patch_cause):
        # Arrange
        mock_cause = Mock()
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
            question_id=self.question_id,
            pk=self.cause_id,
            **self.valid_payload
        )
    
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
    def test_patch_cause_with_invalid_field(self, mock_patch_cause):
        # Arrange - Negative case: Invalid field
        invalid_field_payload = {
            'non_existent_field': 'some value'
        }

        # Act
        response = self.client.patch(
            self.url,
            data=invalid_field_payload,
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

    @patch('cause.serializers.BaseCauses.is_valid')
    def test_patch_cause_validation_error(self, mock_is_valid):
        # Arrange
        mock_is_valid.side_effect = Exception("Validation error")
        
        # Act
        response = self.client.patch(
            self.url,
            data={'invalid': 'data'},
            format='json'
        )
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('cause.services.CausesService.patch_cause')
    @patch('cause.serializers.CausesResponse.__init__')
    def test_patch_cause_response_serialization(self, mock_response_serializer, mock_patch_cause):
        # Arrange
        mock_cause = Mock()
        mock_patch_cause.return_value = mock_cause
        mock_response_serializer.return_value = None  # Constructor returns None
        
        # Act
        response = self.client.patch(
            self.url,
            data=self.valid_payload,
            format='json'
        )
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_response_serializer.assert_called_once_with(mock_cause)
    
    @patch('cause.services.CausesService.patch_cause')
    def test_patch_cause_server_error(self, mock_patch_cause):
        # Arrange
        mock_patch_cause.side_effect = Exception("Unexpected server error")
        
        # Act
        response = self.client.patch(
            self.url,
            data=self.valid_payload,
            format='json'
        )
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)