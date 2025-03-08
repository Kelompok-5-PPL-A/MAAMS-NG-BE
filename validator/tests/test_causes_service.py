from django.test import TestCase
from unittest.mock import patch, Mock
from requests.exceptions import RequestException
from validator.enums import ValidationType
from validator.exceptions import AIServiceErrorException
from validator.services.causes import CausesService

class CausesServiceTest(TestCase):
    @patch('validator.services.causes.Groq')
    def test_api_call_positive(self, mock_groq):
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='true'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        system_message = "You are an AI model. You are asked to determine whether the given cause is the cause of the given problem."
        user_prompt = "Is 'Example cause' the cause of 'Example problem'? Answer only with True/False"
        response = service.api_call(system_message, user_prompt, ValidationType.NORMAL)

        self.assertEqual(response, 1)
        mock_client.chat.completions.create.assert_called_once_with(
            messages=[
                {
                    "role": "system",
                    "content": system_message,
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model="llama-3.3-70b-specdec",
            temperature=0.1,
            max_tokens=50,
            seed=42
        )

    @patch('validator.services.causes.Groq')
    def test_api_call_returns_false(self, mock_groq):
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='false'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        system_message = "You are an AI model. You are asked to determine whether the given cause is the cause of the given problem."
        user_prompt = "Is 'Example cause' the cause of 'Example problem'? Answer only with True/False"
        response = service.api_call(system_message, user_prompt, ValidationType.NORMAL)

        self.assertEqual(response, 0)
        mock_client.chat.completions.create.assert_called_once_with(
            messages=[
                {
                    "role": "system",
                    "content": system_message,
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model="llama-3.3-70b-specdec",
            temperature=0.1,
            max_tokens=50,
            seed=42
        )

    @patch('validator.services.causes.Groq')
    def test_api_call_request_exception(self, mock_groq):
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = RequestException("Network error")
        mock_groq.return_value = mock_client

        service = CausesService()
        system_message = "You are an AI model. You are asked to determine whether the given cause is the cause of the given problem."
        user_prompt = "Is 'Example cause' the cause of 'Example problem'? Answer only with True/False"

        with self.assertRaises(AIServiceErrorException) as context:
            service.api_call(system_message, user_prompt, ValidationType.NORMAL)

        mock_client.chat.completions.create.assert_called_once_with(
            messages=[
                {
                    "role": "system",
                    "content": system_message,
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model="llama-3.3-70b-specdec",
            temperature=0.1,
            max_tokens=50,
            seed=42
        )

        self.assertTrue("Failed to call the AI service." in str(context.exception))

    @patch('validator.services.causes.Groq')
    def test_api_call_negative(self, mock_groq):
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API call failed")
        mock_groq.return_value = mock_client

        service = CausesService()
        system_message = "You are an AI model. You are asked to determine whether the given cause is the cause of the given problem."
        user_prompt = "test prompt"
        with self.assertRaises(Exception):
            service.api_call(system_message, user_prompt, ValidationType.NORMAL)

    @patch('validator.services.causes.Groq')
    def test_api_call_forbidden_access(self, mock_groq):
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("Unauthorized: Invalid API key")
        mock_groq.return_value = mock_client

        service = CausesService()
        system_message = "You are an AI model. You are asked to determine whether the given cause is the cause of the given problem."
        user_prompt = "Test prompt"
        with self.assertRaises(Exception):
            service.api_call(system_message, user_prompt, ValidationType.NORMAL)