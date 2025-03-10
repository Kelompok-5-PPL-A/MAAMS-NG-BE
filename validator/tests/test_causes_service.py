import uuid
from django.test import TestCase
from unittest.mock import patch, Mock
from requests.exceptions import RequestException
from validator.constants import FeedbackMsg
from validator.enums import ValidationType
from validator.exceptions import AIServiceErrorException
from validator.models.causes import Causes
from validator.models.questions import Question
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

    @patch('validator.services.causes.Groq')
    def test_api_call_other_validation_type_returns_1(self, mock_groq):
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='Option 1 is correct'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        system_message = "You are an AI model. You are asked to select the correct option."
        user_prompt = "Which option is correct? Answer with the option number."
        response = service.api_call(system_message, user_prompt, ValidationType.FALSE)

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
    def test_api_call_other_validation_type_returns_2(self, mock_groq):
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='I choose option 2'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        system_message = "You are an AI model. You are asked to select the correct option."
        user_prompt = "Which option is correct? Answer with the option number."
        response = service.api_call(system_message, user_prompt, ValidationType.ROOT_TYPE)

        self.assertEqual(response, 2)
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
    def test_api_call_other_validation_type_returns_3(self, mock_groq):
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='The answer is 3'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        system_message = "You are an AI model. You are asked to select the correct option."
        user_prompt = "Which option is correct? Answer with the option number."
        response = service.api_call(system_message, user_prompt, ValidationType.FALSE)

        self.assertEqual(response, 3)
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
    def test_retrieve_feedback_not_cause_1_row(self, mock_groq):
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='1'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        cause = Causes(problem_id=uuid.uuid4(), cause="False Cause", row=1, column=1)
        problem = Question(question="Test problem")

        service.retrieve_feedback(cause, problem, None)
        self.assertEqual(cause.feedback, FeedbackMsg.FALSE_ROW_1_NOT_CAUSE.format(column='B'))

    @patch('validator.services.causes.Groq')
    def test_retrieve_feedback_positive_neutral_1_row(self, mock_groq):
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='2'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        cause = Causes(problem_id=uuid.uuid4(), cause="Positive/Neutral Cause", row=1, column=1)
        problem = Question(question="Test problem")

        service.retrieve_feedback(cause, problem, None)
        self.assertEqual(cause.feedback, FeedbackMsg.FALSE_ROW_N_POSITIVE_NEUTRAL.format(column='B', row=1))

    @patch('validator.services.causes.Groq')
    def test_retrieve_feedback_not_cause_n_row(self, mock_groq):
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='1'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        prev_cause = Causes(problem_id=uuid.uuid4(), cause="Base Cause", row=1, column=1)
        cause = Causes(problem_id=uuid.uuid4(), cause="False Cause", row=2, column=1)
        problem = Question(question="Test problem")

        service.retrieve_feedback(cause, problem, prev_cause)
        self.assertEqual(cause.feedback, FeedbackMsg.FALSE_ROW_N_NOT_CAUSE.format(column='B', row=2, prev_row=1))

    @patch('validator.services.causes.Groq')
    def test_retrieve_feedback_positive_neutral_n_row(self, mock_groq):
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='2'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        prev_cause = Causes(problem_id=uuid.uuid4(), cause="Base Cause", row=1, column=1)
        cause = Causes(problem_id=uuid.uuid4(), cause="Positive/Neutral Cause", row=2, column=1)
        problem = Question(question="Test problem")

        service.retrieve_feedback(cause, problem, prev_cause)
        self.assertEqual(cause.feedback, FeedbackMsg.FALSE_ROW_N_POSITIVE_NEUTRAL.format(column='B', row=2))

    @patch('validator.services.causes.Groq')
    def test_retrieve_feedback_similar_previous_n_row(self, mock_groq):
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='3'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        cause = Causes(problem_id=uuid.uuid4(), cause="Similar Cause", row=2, column=1)
        prev_cause = Causes(problem_id=uuid.uuid4(), cause="Previous Cause", row=1, column=1)
        problem = Question(question="Test problem")

        service.retrieve_feedback(cause, problem, prev_cause)
        self.assertEqual(cause.feedback, FeedbackMsg.FALSE_ROW_N_SIMILAR_PREVIOUS.format(column='B', row=2))