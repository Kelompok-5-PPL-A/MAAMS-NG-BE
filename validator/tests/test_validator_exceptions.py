from django.test import TestCase
from validator.exceptions import AIServiceErrorException


class AIServiceErrorExceptionTest(TestCase):
    def test_exception_message(self):
        with self.assertRaises(AIServiceErrorException) as context:
            raise AIServiceErrorException("Test error message")
        
        self.assertEqual(str(context.exception), "Test error message") 