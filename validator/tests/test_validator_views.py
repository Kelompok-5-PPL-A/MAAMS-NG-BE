import uuid
from django.test import TestCase
from unittest.mock import patch, Mock
from rest_framework import status
from cause.models import Causes
from question.models import Question
from validator.views import ValidateView


class ValidateViewTest(TestCase):
    def setUp(self):
        self.view = ValidateView()
        self.question_id = uuid.uuid4()
        self.question = Question.objects.create(
            id=self.question_id,
            question="Test question"
        )
        self.cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Test cause",
            row=1,
            column=0,
            status=False
        )

    @patch('validator.services.CausesService.validate')
    def test_patch_success(self, mock_validate):
        mock_validate.return_value = [self.cause]
        request = Mock()
        response = self.view.patch(request, self.question_id)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['cause'], "Test cause") 