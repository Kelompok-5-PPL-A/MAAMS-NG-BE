import uuid
from django.test import TestCase
from unittest.mock import patch, Mock
from requests.exceptions import RequestException
from validator.constants import FeedbackMsg, ErrorMsg
from validator.enums import ValidationType
from validator.exceptions import AIServiceErrorException
from cause.models import Causes
from question.models import Question
from validator.services import CausesService
from django.test import TestCase
from django.core.cache import cache
from validator.services import RateLimiter
import time

class CausesServiceTest(TestCase):
    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_api_call_positive(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='true'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client
        mock_request = Mock()

        service = CausesService()
        system_message = "You are an AI model. You are asked to determine whether the given cause is the cause of the given problem."
        user_prompt = "Is 'Example cause' the cause of 'Example problem'? Answer only with True/False"
        response = service.api_call(system_message, user_prompt, ValidationType.NORMAL, request=mock_request)

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
                model="llama-3.1-8b-instant",
            temperature=0.7,
            max_completion_tokens=8192,
            top_p=0.95,
            stream=False,
            seed=42
        )

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_api_call_returns_false(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='false'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client
        mock_request = Mock()

        service = CausesService()
        system_message = "You are an AI model. You are asked to determine whether the given cause is the cause of the given problem."
        user_prompt = "Is 'Example cause' the cause of 'Example problem'? Answer only with True/False"
        response = service.api_call(system_message, user_prompt, ValidationType.NORMAL, request=mock_request)

        self.assertEqual(response, 0)

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_api_call_request_exception(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = RequestException("Network error")
        mock_groq.return_value = mock_client
        mock_request = Mock()

        service = CausesService()
        system_message = "You are an AI model. You are asked to determine whether the given cause is the cause of the given problem."
        user_prompt = "Is 'Example cause' the cause of 'Example problem'? Answer only with True/False"

        with self.assertRaises(AIServiceErrorException) as context:
            service.api_call(system_message, user_prompt, ValidationType.NORMAL, request=mock_request)

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
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_completion_tokens=8192,
            top_p=0.95,
            stream=False,
            seed=42
        )

        self.assertEqual(str(context.exception), "Failed to call the AI service.")

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_api_call_negative(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API call failed")
        mock_groq.return_value = mock_client

        service = CausesService()
        system_message = "You are an AI model. You are asked to determine whether the given cause is the cause of the given problem."
        user_prompt = "test prompt"
        with self.assertRaises(Exception):
            service.api_call(system_message, user_prompt, ValidationType.NORMAL)

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_api_call_forbidden_access(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("Unauthorized: Invalid API key")
        mock_groq.return_value = mock_client

        service = CausesService()
        system_message = "You are an AI model. You are asked to determine whether the given cause is the cause of the given problem."
        user_prompt = "Test prompt"
        with self.assertRaises(Exception):
            service.api_call(system_message, user_prompt, ValidationType.NORMAL)

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_api_call_validation_type_root(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='true'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client
        mock_request = Mock()

        service = CausesService()
        response = service.api_call(
            system_message="test",
            user_prompt="test",
            validation_type=ValidationType.ROOT,
            request=mock_request
        )
        self.assertEqual(response, 1)

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_api_call_validation_type_root_type(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='2'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client
        mock_request = Mock()

        service = CausesService()
        response = service.api_call(
            system_message="test",
            user_prompt="test",
            validation_type=ValidationType.ROOT_TYPE,
            request=mock_request
        )
        self.assertEqual(response, 2)

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_retrieve_feedback_not_cause_1_row(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='1'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        cause = Causes(question_id=uuid.uuid4(), cause="False Cause", row=1, column=1)
        problem = Question(question="Test problem")
        mock_request = Mock()

        service.retrieve_feedback(cause, problem, None, mock_request)
        self.assertEqual(cause.feedback, FeedbackMsg.FALSE_ROW_1_NOT_CAUSE.format(column='B'))

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_retrieve_feedback_positive_neutral_1_row(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='2'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        cause = Causes(question_id=uuid.uuid4(), cause="Positive/Neutral Cause", row=1, column=1)
        problem = Question(question="Test problem")
        mock_request = Mock()

        service.retrieve_feedback(cause, problem, None, mock_request)
        self.assertEqual(cause.feedback, FeedbackMsg.FALSE_ROW_N_POSITIVE_NEUTRAL.format(column='B', row=1))

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_retrieve_feedback_not_cause_n_row(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='1'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        prev_cause = Causes(question_id=uuid.uuid4(), cause="Base Cause", row=1, column=1)
        cause = Causes(question_id=uuid.uuid4(), cause="False Cause", row=2, column=1)
        problem = Question(question="Test problem")
        mock_request = Mock()

        service.retrieve_feedback(cause, problem, prev_cause, mock_request)
        self.assertEqual(cause.feedback, FeedbackMsg.FALSE_ROW_N_NOT_CAUSE.format(column='B', row=2, prev_row=1))

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_retrieve_feedback_positive_neutral_n_row(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='2'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        prev_cause = Causes(question_id=uuid.uuid4(), cause="Base Cause", row=1, column=1)
        cause = Causes(question_id=uuid.uuid4(), cause="Positive/Neutral Cause", row=2, column=1)
        problem = Question(question="Test problem")
        mock_request = Mock()

        service.retrieve_feedback(cause, problem, prev_cause, mock_request)
        self.assertEqual(cause.feedback, FeedbackMsg.FALSE_ROW_N_POSITIVE_NEUTRAL.format(column='B', row=2))

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_retrieve_feedback_similar_previous_n_row(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='3'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        cause = Causes(question_id=uuid.uuid4(), cause="Similar Cause", row=2, column=1)
        prev_cause = Causes(question_id=uuid.uuid4(), cause="Previous Cause", row=1, column=1)
        problem = Question(question="Test problem")
        mock_request = Mock()

        service.retrieve_feedback(cause, problem, prev_cause, mock_request)
        self.assertEqual(cause.feedback, FeedbackMsg.FALSE_ROW_N_SIMILAR_PREVIOUS.format(column='B', row=2))

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_retrieve_feedback_with_prev_cause(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='1'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        question_id = uuid.uuid4()
        question = Question.objects.create(
            id=question_id,
            question="Test question"
        )
        cause = Causes.objects.create(
            question_id=question_id,
            cause="Test cause",
            row=1,
            column=0,
            status=False
        )
        prev_cause = Causes.objects.create(
            question_id=question_id,
            cause="Previous cause",
            row=0,
            column=0
        )
        mock_request = Mock()

        service.retrieve_feedback(cause, question, prev_cause, mock_request)
        self.assertIn("bukan merupakan sebab", cause.feedback)

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_retrieve_feedback_without_prev_cause(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='2'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        question_id = uuid.uuid4()
        question = Question.objects.create(
            id=question_id,
            question="Test question"
        )
        cause = Causes.objects.create(
            question_id=question_id,
            cause="Test cause",
            row=1,
            column=0,
            status=False
        )
        mock_request = Mock()

        service.retrieve_feedback(cause, question, None, mock_request)
        self.assertIn("sebab positif atau netral", cause.feedback)

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_validate_with_status_true(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        service = CausesService()
        question_id = uuid.uuid4()
        question = Question.objects.create(
            id=question_id,
            question="Test question"
        )
        cause = Causes.objects.create(
            question_id=question_id,
            cause="Test cause",
            row=1,
            column=0,
            status=True
        )
        mock_request = Mock()
        
        service.validate(question_id, mock_request)
        self.assertTrue(cause.status)

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_validate_with_multiple_rows(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='true'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        question_id = uuid.uuid4()
        question = Question.objects.create(
            id=question_id,
            question="Test question"
        )

        first_cause = Causes.objects.create(
            question_id=question_id,
            cause="First cause",
            row=1,
            column=0,
            status=True
        )

        cause = Causes.objects.create(
            question_id=question_id,
            cause="Test cause",
            row=2,
            column=0,
            status=False
        )
        mock_request = Mock()

        def mock_api_call_side_effect(system_message, user_prompt, validation_type, request=None):
            if validation_type == ValidationType.NORMAL:
                return 1
            elif validation_type == ValidationType.ROOT:
                return 0
            return 0

        with patch.object(CausesService, 'api_call', side_effect=mock_api_call_side_effect) as mock_api_call:
            service.validate(question_id, mock_request)
            cause.refresh_from_db()
            self.assertTrue(cause.status)
            
            mock_api_call.assert_any_call(
                system_message="You are an AI model. You are asked to determine whether the given cause is the cause of the given problem.",
                user_prompt=f"Is '{cause.cause}' the cause of '{first_cause.cause}'? Answer only with True/False",
                validation_type=ValidationType.NORMAL,
                request=mock_request
            )

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_check_root_cause_with_korupsi_categories(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='true'))]
        mock_client.chat.completions.create.side_effect = [
            Mock(choices=[Mock(message=Mock(content='true'))]),
            Mock(choices=[Mock(message=Mock(content='2'))])
        ]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client
        mock_request = Mock()

        service = CausesService()
        question_id = uuid.uuid4()
        question = Question.objects.create(
            id=question_id,
            question="Test question"
        )
        cause = Causes.objects.create(
            question_id=question_id,
            cause="Test cause",
            row=1,
            column=0,
            status=False
        )

        service.check_root_cause(cause, question, mock_request)
        cause.refresh_from_db()
        self.assertTrue(cause.root_status)
        self.assertIn("Korupsi Tahta", cause.feedback)

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_check_root_cause_default_korupsi(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='true'))]
        mock_client.chat.completions.create.side_effect = [
            Mock(choices=[Mock(message=Mock(content='true'))]),
            Mock(choices=[Mock(message=Mock(content='4'))])
        ]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client
        mock_request = Mock()

        service = CausesService()
        question_id = uuid.uuid4()
        question = Question.objects.create(
            id=question_id,
            question="Test question"
        )
        cause = Causes.objects.create(
            question_id=question_id,
            cause="Test cause",
            row=1,
            column=0,
            status=False
        )

        service.check_root_cause(cause, question, mock_request)
        cause.refresh_from_db()
        self.assertTrue(cause.root_status)
        self.assertIn("Korupsi Harta", cause.feedback)

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_validate_with_row_1(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='true'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        question_id = uuid.uuid4()
        question = Question.objects.create(
            id=question_id,
            question="Test question"
        )
        cause = Causes.objects.create(
            question_id=question_id,
            cause="Test cause",
            row=1,
            column=0,
            status=False
        )
        mock_request = Mock()

        def mock_api_call_side_effect(system_message, user_prompt, validation_type, request=None):
            if validation_type == ValidationType.NORMAL:
                return 1
            return 0

        with patch.object(CausesService, 'api_call', side_effect=mock_api_call_side_effect) as mock_api_call:
            service.validate(question_id, mock_request)
            cause.refresh_from_db()
            self.assertTrue(cause.status)
            
            mock_api_call.assert_any_call(
                system_message="You are an AI model. You are asked to determine whether the given cause is the cause of the given problem.",
                user_prompt=f"Is '{cause.cause}' the cause of this question: '{question.question}'? Answer only with True/False",
                validation_type=ValidationType.NORMAL,
                request=mock_request
            )

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_validate_returns_false(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='false'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client

        service = CausesService()
        question_id = uuid.uuid4()
        question = Question.objects.create(
            id=question_id,
            question="Test question"
        )
        first_cause = Causes.objects.create(
            question_id=question_id,
            cause="First cause",
            row=1,
            column=0,
            status=True
        )
        cause = Causes.objects.create(
            question_id=question_id,
            cause="Test cause",
            row=2,
            column=0,
            status=False
        )
        mock_request = Mock()

        def mock_api_call_side_effect(system_message, user_prompt, validation_type, request=None):
            return 0

        with patch.object(CausesService, 'api_call', side_effect=mock_api_call_side_effect) as mock_api_call:
            service.validate(question_id, mock_request)
            cause.refresh_from_db()
            self.assertFalse(cause.status)

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_check_root_cause_with_korupsi_harta(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='true'))]
        mock_client.chat.completions.create.side_effect = [
            Mock(choices=[Mock(message=Mock(content='true'))]),
            Mock(choices=[Mock(message=Mock(content='1'))])
        ]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client
        mock_request = Mock()

        service = CausesService()
        question_id = uuid.uuid4()
        question = Question.objects.create(
            id=question_id,
            question="Test question"
        )
        cause = Causes.objects.create(
            question_id=question_id,
            cause="Test cause",
            row=1,
            column=0,
            status=False
        )

        service.check_root_cause(cause, question, mock_request)
        cause.refresh_from_db()
        self.assertTrue(cause.root_status)
        self.assertIn("Korupsi Harta", cause.feedback)

    @patch('validator.services.Groq')
    @patch('validator.services.RateLimiter.is_allowed')
    def test_check_root_cause_with_korupsi_cinta(self, mock_is_allowed, mock_groq):
        mock_is_allowed.return_value = True
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='true'))]
        mock_client.chat.completions.create.side_effect = [
            Mock(choices=[Mock(message=Mock(content='true'))]),
            Mock(choices=[Mock(message=Mock(content='3'))])
        ]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client
        mock_request = Mock()

        service = CausesService()
        question_id = uuid.uuid4()
        question = Question.objects.create(
            id=question_id,
            question="Test question"
        )
        cause = Causes.objects.create(
            question_id=question_id,
            cause="Test cause",
            row=1,
            column=0,
            status=False
        )

        service.check_root_cause(cause, question, mock_request)
        cause.refresh_from_db()
        self.assertTrue(cause.root_status)
        self.assertIn("Korupsi Cinta", cause.feedback)

class RateLimiterTest(TestCase):
    def setUp(self):
        # Clear cache before each test
        cache.clear()
        # Create test rate limiter with 3 requests per 2 seconds
        self.rate_limiter = RateLimiter(rate=3, per=2)
        # Test user identifier
        self.test_user = "test_user_123"
    
    def tearDown(self):
        # Clear cache after each test
        cache.clear()
    
    def test_first_request_allowed(self):
        """Test that the first request is always allowed"""
        self.assertTrue(self.rate_limiter.is_allowed(self.test_user))
        
        # Verify the counter is set to 1
        key = f"ratelimit:{self.test_user}"
        self.assertEqual(cache.get(key), 1)
    
    def test_under_limit_requests_allowed(self):
        """Test that requests under the limit are allowed"""
        # Make 3 requests (at the limit)
        for i in range(3):
            self.assertTrue(self.rate_limiter.is_allowed(self.test_user))
        
        # Verify the counter is set to 3
        key = f"ratelimit:{self.test_user}"
        self.assertEqual(cache.get(key), 3)
    
    def test_over_limit_requests_blocked(self):
        """Test that requests over the limit are blocked"""
        # Make 3 requests (at the limit)
        for i in range(3):
            self.assertTrue(self.rate_limiter.is_allowed(self.test_user))
        
        # The 4th request should be blocked
        self.assertFalse(self.rate_limiter.is_allowed(self.test_user))
        
        # Verify the counter is still 4 (it increments even when blocked)
        key = f"ratelimit:{self.test_user}"
        self.assertEqual(cache.get(key), 4)
    
    def test_limit_reset_after_expiry(self):
        """Test that the limit resets after expiry time"""
        # Make 3 requests (at the limit)
        for i in range(3):
            self.assertTrue(self.rate_limiter.is_allowed(self.test_user))
        
        # The 4th request should be blocked
        self.assertFalse(self.rate_limiter.is_allowed(self.test_user))
        
        # Wait for cache expiry (use a shorter time for tests)
        time.sleep(2)
        
        # After expiry, new request should be allowed
        self.assertTrue(self.rate_limiter.is_allowed(self.test_user))
        
        # Counter should be reset to 1
        key = f"ratelimit:{self.test_user}"
        self.assertEqual(cache.get(key), 1)
    
    def test_different_users_have_separate_limits(self):
        """Test that different users have separate rate limits"""
        # First user makes max requests
        for i in range(3):
            self.assertTrue(self.rate_limiter.is_allowed(self.test_user))
        
        # First user is now blocked
        self.assertFalse(self.rate_limiter.is_allowed(self.test_user))
        
        # Second user should still be allowed
        second_user = "another_test_user"
        self.assertTrue(self.rate_limiter.is_allowed(second_user))
        
        # Verify separate counters
        self.assertEqual(cache.get(f"ratelimit:{self.test_user}"), 4)
        self.assertEqual(cache.get(f"ratelimit:{second_user}"), 1)
    
    def test_custom_rate_limits(self):
        """Test that custom rate limits work correctly"""
        # Create a stricter rate limiter (2 requests per 5 seconds)
        strict_limiter = RateLimiter(rate=2, per=5)
        
        # First 2 requests are allowed
        self.assertTrue(strict_limiter.is_allowed(self.test_user))
        self.assertTrue(strict_limiter.is_allowed(self.test_user))
        
        # Third request is blocked
        self.assertFalse(strict_limiter.is_allowed(self.test_user))
        
        # Regular limiter should still allow 3 requests
        another_user = "yet_another_user"
        self.assertTrue(self.rate_limiter.is_allowed(another_user))
        self.assertTrue(self.rate_limiter.is_allowed(another_user))
        self.assertTrue(self.rate_limiter.is_allowed(another_user))
        self.assertFalse(self.rate_limiter.is_allowed(another_user))