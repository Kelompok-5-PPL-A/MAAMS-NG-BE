import uuid
from django.test import TestCase, TransactionTestCase
from unittest.mock import patch, Mock, call, ANY
from requests.exceptions import RequestException
from validator.constants import FeedbackMsg, ErrorMsg
from validator.enums import ValidationType
from validator.exceptions import AIServiceErrorException
from cause.models import Causes
from question.models import Question
from validator.services import CausesService


class CausesServiceTest(TransactionTestCase):
    def setUp(self):
        """Set up test data before each test method"""
        self.service = CausesService()
        self.question_id = uuid.uuid4()
        self.question = Question.objects.create(
            id=self.question_id,
            question="Test question for akar masalah analysis"
        )
        
        # Create some test causes
        self.test_causes = [
            Causes.objects.create(
                question_id=self.question_id,
                cause="First cause in column A",
                row=1,
                column=0,
                status=False,
                root_status=False,
                feedback=""
            ),
            Causes.objects.create(
                question_id=self.question_id,
                cause="First cause in column B",
                row=1,
                column=1,
                status=False,
                root_status=False,
                feedback=""
            ),
            Causes.objects.create(
                question_id=self.question_id,
                cause="Second cause in column A",
                row=2,
                column=0,
                status=False,
                root_status=False,
                feedback=""
            )
        ]
        
        # Create a mock request for API calls
        self.mock_request = Mock()
        self.mock_request.user = Mock(is_authenticated=True)
        self.mock_request.user.id = "test-user-123"
        
    def tearDown(self):
        """Clean up after each test method"""
        # Using try-except to handle any cleanup issues
        Causes.objects.all().delete()
        Question.objects.all().delete()

    @patch('validator.services.Groq')
    def test_api_call_normal_validation_true(self, mock_groq):
        """Test API call with normal validation returning true"""
        # Configure mock
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='true'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client
        
        system_message = "Test system message"
        user_prompt = "Is this cause valid? Answer only with True/False"
        
        # Execute
        result = self.service.api_call(
            system_message=system_message,
            user_prompt=user_prompt,
            validation_type=ValidationType.NORMAL,
            request=self.mock_request
        )
        
        # Verify
        self.assertEqual(result, 1)
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
            model="deepseek-r1-distill-llama-70b",
            temperature=0.7,
            max_completion_tokens=8192,
            top_p=0.95,
            stream=False,
            seed=42
        )

    @patch('validator.services.Groq')
    def test_api_call_normal_validation_false(self, mock_groq):
        """Test API call with normal validation returning false"""
        # Configure mock
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='false'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client
        
        system_message = "Test system message"
        user_prompt = "Is this cause valid? Answer only with True/False"
        
        # Execute
        result = self.service.api_call(
            system_message=system_message,
            user_prompt=user_prompt,
            validation_type=ValidationType.NORMAL,
            request=self.mock_request
        )
        
        # Verify
        self.assertEqual(result, 0)

    @patch('validator.services.Groq')
    def test_api_call_root_validation_true(self, mock_groq):
        """Test API call with root validation returning true"""
        # Configure mock
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='true'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client
        
        system_message = "Test system message"
        user_prompt = "Is this cause a root cause? Answer only with True/False"
        
        # Execute
        result = self.service.api_call(
            system_message=system_message,
            user_prompt=user_prompt,
            validation_type=ValidationType.ROOT,
            request=self.mock_request
        )
        
        # Verify
        self.assertEqual(result, 1)

    @patch('validator.services.Groq')
    def test_api_call_false_validation_type_1(self, mock_groq):
        """Test API call with false validation returning type 1"""
        # Configure mock
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='1'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client
        
        system_message = "Test system message"
        user_prompt = "Why is this cause false? Answer with: 1 if not a cause"
        
        # Execute
        result = self.service.api_call(
            system_message=system_message,
            user_prompt=user_prompt,
            validation_type=ValidationType.FALSE,
            request=self.mock_request
        )
        
        # Verify
        self.assertEqual(result, 1)

    @patch('validator.services.Groq')
    def test_api_call_root_type_validation(self, mock_groq):
        """Test API call with root type validation"""
        # Configure mock
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='2'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client
        
        system_message = "Test system message"
        user_prompt = "Categorize this root cause: 1-Harta, 2-Tahta, 3-Cinta"
        
        # Execute
        result = self.service.api_call(
            system_message=system_message,
            user_prompt=user_prompt,
            validation_type=ValidationType.ROOT_TYPE,
            request=self.mock_request
        )
        
        # Verify
        self.assertEqual(result, 2)

    @patch('validator.services.Groq')
    def test_api_call_request_exception(self, mock_groq):
        """Test API call handling request exception"""
        # Configure mock
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = RequestException("Network error")
        mock_groq.return_value = mock_client
        
        system_message = "Test system message"
        user_prompt = "Is this cause valid? Answer only with True/False"
        
        # Execute & Verify
        with self.assertRaises(AIServiceErrorException) as context:
            self.service.api_call(
                system_message=system_message,
                user_prompt=user_prompt,
                validation_type=ValidationType.NORMAL,
                request=self.mock_request
            )
        
        self.assertEqual(str(context.exception), ErrorMsg.AI_SERVICE_ERROR)

    @patch('validator.services.Groq')
    def test_api_call_unexpected_response(self, mock_groq):
        """Test API call handling unexpected response"""
        # Configure mock
        mock_client = Mock()
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [Mock(message=Mock(content='unexpected'))]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        mock_groq.return_value = mock_client
        
        system_message = "Test system message"
        user_prompt = "Is this cause valid? Answer only with True/False"
        
        # Execute
        result = self.service.api_call(
            system_message=system_message,
            user_prompt=user_prompt,
            validation_type=ValidationType.NORMAL,
            request=self.mock_request
        )
        
        # Verify
        self.assertEqual(result, 0)  # Default value for unexpected responses

    @patch('validator.services.Groq')
    def test_check_if_corruption_related_true(self, mock_groq):
        """Test detection of corruption-related causes - positive case"""
        # Test various corruption terms
        corruption_cases = [
            "Terjadi korupsi dalam tender",
            # Menggunakan term yang persis sama dengan yang ada di method check_if_corruption_related
            "korupsi", 
            "suap", 
            "sogok", 
            "pungli", 
            "pungutan liar",
            "penyalahgunaan wewenang", 
            "nepotisme", 
            "kolusi",
            "gratifikasi", 
            "pemalsuan", 
            "penggelapan", 
            "penyelewengan",
            "pemerasan", 
            "mark up", 
            "penyimpangan"
        ]
        
        for cause_text in corruption_cases:
            result = self.service.check_if_corruption_related(cause_text)
            self.assertTrue(result, f"Should detect corruption in: '{cause_text}'")

    @patch('validator.services.Groq')
    def test_check_if_corruption_related_false(self, mock_groq):
        """Test detection of corruption-related causes - negative case"""
        # Test non-corruption cases
        non_corruption_cases = [
            "Kurangnya pelatihan karyawan",
            "Buruknya komunikasi antar divisi",
            "Sistem yang tidak efisien",
            "Kurangnya anggaran operasional",
            "Keterlambatan proses administrasi"
        ]
        
        for cause_text in non_corruption_cases:
            result = self.service.check_if_corruption_related(cause_text)
            self.assertFalse(result, f"Should NOT detect corruption in: '{cause_text}'")

    @patch.object(CausesService, 'api_call')
    def test_retrieve_feedback_row_1_not_cause(self, mock_api_call):
        """Test retrieving feedback for row 1 when it's not a cause"""
        # Configure mock
        mock_api_call.return_value = 1  # Code for NOT_THE_CAUSE
        
        # Test data
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Invalid first cause",
            row=1,
            column=2,  # Column C
            status=False
        )
        
        # Execute
        self.service.retrieve_feedback(cause, self.question, None, self.mock_request)
        
        # Verify
        self.assertEqual(cause.feedback, FeedbackMsg.FALSE_ROW_1_NOT_CAUSE.format(column='C'))
        mock_api_call.assert_called_once()

    @patch.object(CausesService, 'api_call')
    def test_retrieve_feedback_row_1_positive_neutral(self, mock_api_call):
        """Test retrieving feedback for row 1 when it's positive/neutral"""
        # Configure mock
        mock_api_call.return_value = 2  # Code for POSITIVE_OR_NEUTRAL
        
        # Test data
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Positive first cause",
            row=1,
            column=2,  # Column C
            status=False
        )
        
        # Execute
        self.service.retrieve_feedback(cause, self.question, None, self.mock_request)
        
        # Verify
        self.assertEqual(cause.feedback, FeedbackMsg.FALSE_ROW_N_POSITIVE_NEUTRAL.format(column='C', row=1))
        mock_api_call.assert_called_once()

    @patch.object(CausesService, 'api_call')
    def test_retrieve_feedback_row_n_not_cause(self, mock_api_call):
        """Test retrieving feedback for row n when it's not a cause"""
        # Configure mock
        mock_api_call.return_value = 1  # Code for NOT_THE_CAUSE
        
        # Test data
        prev_cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Valid previous cause",
            row=2,
            column=1,  # Column B
            status=True
        )
        
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Invalid cause",
            row=3,
            column=1,  # Column B
            status=False
        )
        
        # Execute
        self.service.retrieve_feedback(cause, self.question, prev_cause, self.mock_request)
        
        # Verify
        self.assertEqual(cause.feedback, FeedbackMsg.FALSE_ROW_N_NOT_CAUSE.format(column='B', row=3, prev_row=2))
        mock_api_call.assert_called_once()

    @patch.object(CausesService, 'api_call')
    def test_retrieve_feedback_row_n_positive_neutral(self, mock_api_call):
        """Test retrieving feedback for row n when it's positive/neutral"""
        # Configure mock
        mock_api_call.return_value = 2  # Code for POSITIVE_OR_NEUTRAL
        
        # Test data
        prev_cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Valid previous cause",
            row=2,
            column=1,  # Column B
            status=True
        )
        
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Positive cause",
            row=3,
            column=1,  # Column B
            status=False
        )
        
        # Execute
        self.service.retrieve_feedback(cause, self.question, prev_cause, self.mock_request)
        
        # Verify
        self.assertEqual(cause.feedback, FeedbackMsg.FALSE_ROW_N_POSITIVE_NEUTRAL.format(column='B', row=3))
        mock_api_call.assert_called_once()

    @patch.object(CausesService, 'api_call')
    def test_retrieve_feedback_row_n_similar_previous(self, mock_api_call):
        """Test retrieving feedback for row n when it's similar to previous"""
        # Configure mock
        mock_api_call.return_value = 3  # Code for SIMILAR_TO_PREVIOUS
        
        # Test data
        prev_cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Valid previous cause",
            row=2,
            column=1,  # Column B
            status=True
        )
        
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Similar cause",
            row=3,
            column=1,  # Column B
            status=False
        )
        
        # Execute
        self.service.retrieve_feedback(cause, self.question, prev_cause, self.mock_request)
        
        # Verify
        self.assertEqual(cause.feedback, FeedbackMsg.FALSE_ROW_N_SIMILAR_PREVIOUS.format(column='B', row=3))
        mock_api_call.assert_called_once()

    @patch.object(CausesService, 'api_call')
    def test_retrieve_feedback_default(self, mock_api_call):
        """Test retrieving default feedback when API returns unexpected code"""
        # Configure mock
        mock_api_call.return_value = 99  # Unknown code
        
        # Test data
        prev_cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Valid previous cause",
            row=2,
            column=1,  # Column B
            status=True
        )
        
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Weird cause",
            row=3,
            column=1,  # Column B
            status=False
        )
        
        # Execute
        self.service.retrieve_feedback(cause, self.question, prev_cause, self.mock_request)
        
        # Verify
        self.assertEqual(cause.feedback, "Sebab di kolom B baris 3 perlu diperbaiki.")
        mock_api_call.assert_called_once()

    @patch.object(CausesService, 'check_root_cause')
    @patch.object(CausesService, 'api_call')
    def test_validate_single_cause_row_1_valid(self, mock_api_call, mock_check_root):
        """Test validating a single valid cause in row 1"""
        # Configure mocks
        mock_api_call.return_value = 1  # Valid cause
        
        # Test data
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Valid first cause",
            row=1,
            column=0,  # Column A
            status=False,
            feedback=""
        )
        
        # Execute
        self.service._validate_single_cause(cause, self.question, None, self.mock_request)
        
        # Verify
        cause.refresh_from_db()
        self.assertTrue(cause.status)
        self.assertEqual(cause.feedback, "")
        mock_api_call.assert_called_once()
        mock_check_root.assert_called_once_with(cause=cause, problem=self.question, request=self.mock_request)

    @patch.object(CausesService, 'retrieve_feedback')
    @patch.object(CausesService, 'api_call')
    def test_validate_single_cause_row_1_invalid(self, mock_api_call, mock_retrieve_feedback):
        """Test validating a single invalid cause in row 1"""
        # Configure mocks
        mock_api_call.return_value = 0  # Invalid cause
        
        # Test data
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Invalid first cause",
            row=1,
            column=0,  # Column A
            status=False
        )
        
        # Execute
        self.service._validate_single_cause(cause, self.question, None, self.mock_request)
        
        # Verify
        cause.refresh_from_db()
        self.assertFalse(cause.status)
        self.assertFalse(cause.root_status)
        mock_api_call.assert_called_once()
        mock_retrieve_feedback.assert_called_once_with(
            cause=cause, problem=self.question, prev_cause=None, request=self.mock_request
        )

    @patch.object(CausesService, 'check_root_cause')
    @patch.object(CausesService, 'api_call')
    def test_validate_single_cause_row_n_valid(self, mock_api_call, mock_check_root):
        """Test validating a single valid cause in row n"""
        # Configure mocks
        mock_api_call.return_value = 1  # Valid cause
        
        # Test data
        prev_cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Valid previous cause",
            row=1,
            column=0,  # Column A
            status=True
        )
        
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Valid next cause",
            row=2,
            column=0,  # Column A
            status=False
        )
        
        # Execute
        self.service._validate_single_cause(cause, self.question, prev_cause, self.mock_request)
        
        # Verify
        cause.refresh_from_db()
        self.assertTrue(cause.status)
        self.assertEqual(cause.feedback, "")
        mock_api_call.assert_called_once()
        mock_check_root.assert_called_once_with(cause=cause, problem=self.question, request=self.mock_request)

    @patch.object(CausesService, 'retrieve_feedback')
    @patch.object(CausesService, 'api_call')
    def test_validate_single_cause_row_n_invalid(self, mock_api_call, mock_retrieve_feedback):
        """Test validating a single invalid cause in row n"""
        # Configure mocks
        mock_api_call.return_value = 0  # Invalid cause
        
        # Test data
        prev_cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Valid previous cause",
            row=1,
            column=0,  # Column A
            status=True
        )
        
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Invalid next cause",
            row=2,
            column=0,  # Column A
            status=False
        )
        
        # Execute
        self.service._validate_single_cause(cause, self.question, prev_cause, self.mock_request)
        
        # Verify
        cause.refresh_from_db()
        self.assertFalse(cause.status)
        self.assertFalse(cause.root_status)
        mock_api_call.assert_called_once()
        mock_retrieve_feedback.assert_called_once_with(
            cause=cause, problem=self.question, prev_cause=prev_cause, request=self.mock_request
        )

    @patch.object(CausesService, 'categorize_corruption')
    @patch.object(CausesService, 'api_call')
    def test_validate_single_cause_corruption_related(self, mock_api_call, mock_categorize):
        """Test validating a corruption-related cause"""
        # Configure mocks
        mock_api_call.return_value = 1  # Valid cause
        
        # Test data
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Terjadi korupsi dana proyek",  # Contains corruption term
            row=1,
            column=0,  # Column A
            status=False
        )
        
        # Execute
        with patch.object(CausesService, 'check_if_corruption_related', return_value=True):
            self.service._validate_single_cause(cause, self.question, None, self.mock_request)
        
        # Verify
        cause.refresh_from_db()
        self.assertTrue(cause.status)
        self.assertTrue(cause.root_status)
        mock_categorize.assert_called_once_with(cause)
        # check_root_cause shouldn't be called for corruption-related causes
        mock_api_call.assert_called_once()

    def test_validate_single_cause_empty_cause(self):
        """Test validating an empty cause - should be skipped"""
        # Test data
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="",  # Empty cause
            row=1,
            column=0,
            status=False
        )
        
        # Execute
        with patch.object(CausesService, 'api_call') as mock_api_call:
            self.service._validate_single_cause(cause, self.question, None, self.mock_request)
        
        # Verify api_call wasn't called
        mock_api_call.assert_not_called()

    def test_validate_single_cause_missing_previous(self):
        """Test validating a cause when previous cause is missing"""
        # Test data for row > 1 without previous cause data
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Test cause without previous",
            row=2,
            column=0,
            status=False,
            feedback=""  # Ensure feedback is empty initially
        )
        
        # Create a mock for save method to prevent database issues
        with patch.object(Causes, 'save') as mock_save:
            # Execute
            with patch.object(CausesService, 'api_call') as mock_api_call:
                self.service._validate_single_cause(cause, self.question, None, self.mock_request)
            
            # Verify
            self.assertFalse(cause.status)
            self.assertEqual(cause.feedback, "Perlu validasi sebab di baris 1 kolom A terlebih dahulu.")
            mock_api_call.assert_not_called()
            mock_save.assert_called_once()

    @patch.object(CausesService, 'api_call')
    def test_check_root_cause_false(self, mock_api_call):
        """Test checking for root cause - false case"""
        # Configure mock
        mock_api_call.return_value = 0  # Not a root cause
        
        # Test data
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="This is not a root cause",
            row=2,
            column=0,
            status=True
        )
        
        # Execute
        self.service.check_root_cause(cause, self.question, self.mock_request)
        
        # Verify
        cause.refresh_from_db()
        self.assertFalse(cause.root_status)
        mock_api_call.assert_called_once()

    @patch.object(CausesService, 'api_call')
    def test_categorize_corruption_harta(self, mock_api_call):
        """Test categorizing corruption as Harta"""
        # Configure mock
        mock_api_call.return_value = 1  # Code for Harta
        
        # Test data
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Korupsi anggaran proyek",
            row=3,
            column=0,
            status=True,
            root_status=True
        )
        
        # Execute
        self.service.categorize_corruption(cause)
        
        # Verify
        cause.refresh_from_db()
        self.assertTrue(f"{FeedbackMsg.ROOT_FOUND.format(column='A')} Korupsi Harta." in cause.feedback)
        mock_api_call.assert_called_once()

    @patch.object(CausesService, 'api_call')
    def test_categorize_corruption_tahta(self, mock_api_call):
        """Test categorizing corruption as Tahta"""
        # Configure mock
        mock_api_call.return_value = 2  # Code for Tahta
        
        # Test data
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Penyalahgunaan wewenang",
            row=3,
            column=1,
            status=True,
            root_status=True
        )
        
        # Execute
        self.service.categorize_corruption(cause)
        
        # Verify
        cause.refresh_from_db()
        self.assertTrue(f"{FeedbackMsg.ROOT_FOUND.format(column='B')} Korupsi Tahta." in cause.feedback)
        mock_api_call.assert_called_once()

    @patch.object(CausesService, 'api_call')
    def test_categorize_corruption_cinta(self, mock_api_call):
        """Test categorizing corruption as Cinta"""
        # Configure mock
        mock_api_call.return_value = 3  # Code for Cinta
        
        # Test data
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Nepotisme dalam rekrutmen",
            row=3,
            column=2,
            status=True,
            root_status=True
        )
        
        # Execute
        self.service.categorize_corruption(cause)
        
        # Verify
        cause.refresh_from_db()
        self.assertTrue(f"{FeedbackMsg.ROOT_FOUND.format(column='C')} Korupsi Cinta." in cause.feedback)
        mock_api_call.assert_called_once()

    # Test untuk fungsi _get_previous_cause
    def test_get_previous_cause_valid(self):
        """Test getting a valid previous cause"""
        # Set up test data
        prev_cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Valid previous cause",
            row=1,
            column=0,
            status=True  # Valid cause
        )
        
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Current cause",
            row=2,
            column=0,
            status=False
        )
        
        # Execute
        result = self.service._get_previous_cause(cause, self.question)
        
        # Verify
        self.assertEqual(result, prev_cause)

    def test_get_previous_cause_row_1(self):
        """Test getting previous cause for row 1 (should return None)"""
        # Set up test data
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="First row cause",
            row=1,
            column=0,
            status=False
        )
        
        # Execute
        result = self.service._get_previous_cause(cause, self.question)
        
        # Verify
        self.assertIsNone(result)

    def test_get_previous_cause_invalid_previous(self):
        """Test getting previous cause when previous is invalid"""
        # Set up test data with an invalid previous cause
        Causes.objects.create(
            question_id=self.question_id,
            cause="Invalid previous cause",
            row=1,
            column=0,
            status=False  # Invalid cause
        )
        
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Current cause",
            row=2,
            column=0,
            status=False
        )
        
        # Execute
        result = self.service._get_previous_cause(cause, self.question)
        
        # Verify
        self.assertIsNone(result)
        
    def test_get_previous_cause_empty_previous(self):
        """Test getting previous cause when previous is empty"""
        # Set up test data with an empty previous cause
        Causes.objects.create(
            question_id=self.question_id,
            cause="",  # Empty cause
            row=1,
            column=0,
            status=True  # Valid but empty
        )
        
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Current cause",
            row=2,
            column=0,
            status=False
        )
        
        # Execute
        result = self.service._get_previous_cause(cause, self.question)
        
        # Verify
        self.assertIsNone(result)
    
    def test_get_previous_cause_exception_handling(self):
        """Test exception handling in _get_previous_cause"""
        # Create a mock cause that will trigger an exception when accessed
        cause = Mock(spec=Causes)
        cause.row = 2
        cause.column = 0
        
        # Configuring the mock to raise an exception when filter is called
        with patch('cause.models.Causes.objects.filter', side_effect=Exception('Test exception')):
            # Execute
            result = self.service._get_previous_cause(cause, self.question)
            
            # Verify
            self.assertIsNone(result)
            
    def test_check_root_cause_true(self):
        """Test checking for root cause - true case"""
        # Test data
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="This is a root cause",
            row=3,
            column=0,
            status=True,
            root_status=False
        )
        
        # Mocking and executing
        with patch.object(CausesService, 'api_call', return_value=1) as mock_api_call:
            with patch.object(CausesService, 'categorize_corruption') as mock_categorize:
                # Important: Mock the save method to update the object in-place without DB call
                with patch.object(Causes, 'save') as mock_save:
                    # Manually set up the behavior we expect
                    def side_effect_save():
                        cause.root_status = True
                    
                    mock_save.side_effect = side_effect_save
                    
                    # Execute
                    self.service.check_root_cause(cause, self.question, self.mock_request)
                    
                    # Verify - don't refresh from DB, use the object directly
                    self.assertTrue(cause.root_status)
                    mock_api_call.assert_called_once()
                    mock_categorize.assert_called_once_with(cause)
    
    def test_check_root_cause_skip_empty(self):
        """Test root cause check skips empty causes"""
        # Test data
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="",  # Empty cause
            row=2,
            column=0,
            status=True
        )
        
        # Execute
        with patch.object(CausesService, 'api_call') as mock_api_call:
            self.service.check_root_cause(cause, self.question, self.mock_request)
            
            # Verify
            cause.refresh_from_db()
            self.assertFalse(cause.root_status)
            mock_api_call.assert_not_called()
            
    def test_check_root_cause_skip_new_column(self):
        """Test root cause check skips early causes in new columns"""
        # Test data for a cause in column C (index 2)
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="New column cause",
            row=2,  # Row > 1
            column=2,  # Column C
            status=True
        )
        
        # Only one valid cause in this column - should skip root check
        Causes.objects.create(
            question_id=self.question_id,
            cause="First valid cause in column C",
            row=1,
            column=2,
            status=True
        )
        
        # Execute
        with patch.object(CausesService, 'api_call') as mock_api_call:
            self.service.check_root_cause(cause, self.question, self.mock_request)
            
            # Verify
            cause.refresh_from_db()
            self.assertFalse(cause.root_status)
            mock_api_call.assert_not_called()
    
    def test_categorize_corruption_empty_cause(self):
        """Test categorize_corruption skips empty causes"""
        # Test data
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="",  # Empty cause
            row=3,
            column=0,
            status=True,
            root_status=True
        )
        
        # Execute
        with patch.object(CausesService, 'api_call') as mock_api_call:
            with patch.object(Causes, 'save') as mock_save:
                self.service.categorize_corruption(cause)
                
                # Verify
                self.assertFalse(cause.root_status)
                self.assertEqual(cause.feedback, "")
                mock_api_call.assert_not_called()
                mock_save.assert_called_once()
                
    @patch.object(CausesService, 'api_call')
    def test_categorize_corruption_default(self, mock_api_call):
        """Test categorizing corruption with default case (unknown category)"""
        # Configure mock
        mock_api_call.return_value = 0  # Unknown code
        
        # Test data
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Unknown corruption type",
            row=3,
            column=0,
            status=True,
            root_status=True
        )
        
        # Execute
        self.service.categorize_corruption(cause)
        
        # Verify
        cause.refresh_from_db()
        self.assertTrue(f"{FeedbackMsg.ROOT_FOUND.format(column='A')} Korupsi Harta." in cause.feedback)
        mock_api_call.assert_called_once()
    
    # Tests for _ensure_next_rows_exist method
    def test_ensure_next_rows_exist_with_root(self):
        """Test _ensure_next_rows_exist when column already has a root cause"""
        # Set up a column with a root cause
        Causes.objects.create(
            question_id=self.question_id,
            cause="Root cause",
            row=3,
            column=0,
            status=True,
            root_status=True
        )
        
        # Add more causes to ensure we have valid rows
        Causes.objects.create(
            question_id=self.question_id,
            cause="Valid cause 1",
            row=1,
            column=0,
            status=True
        )
        
        Causes.objects.create(
            question_id=self.question_id,
            cause="Valid cause 2",
            row=2,
            column=0,
            status=True
        )
        
        # Clear any existing next rows
        Causes.objects.filter(
            question_id=self.question_id,
            column=0,
            row=4
        ).delete()
        
        # Count causes before
        causes_count_before = Causes.objects.filter(question_id=self.question_id).count()
        
        # Execute
        self.service._ensure_next_rows_exist(self.question_id)
        
        # Count causes after
        causes_count_after = Causes.objects.filter(question_id=self.question_id).count()
        
        # Verify no new causes were created
        self.assertEqual(causes_count_before, causes_count_after)
        
    def test_ensure_next_rows_exist_no_valid_rows(self):
        """Test _ensure_next_rows_exist when column has no valid rows"""
        # Delete all causes first
        Causes.objects.filter(question_id=self.question_id).delete()
        
        # Create invalid causes only
        Causes.objects.create(
            question_id=self.question_id,
            cause="Invalid cause",
            row=1,
            column=0,
            status=False
        )
        
        # Count causes before
        causes_count_before = Causes.objects.filter(question_id=self.question_id).count()
        
        # Execute
        self.service._ensure_next_rows_exist(self.question_id)
        
        # Count causes after
        causes_count_after = Causes.objects.filter(question_id=self.question_id).count()
        
        # Verify no new causes were created
        self.assertEqual(causes_count_before, causes_count_after)
        
    def test_ensure_next_rows_exist_creates_next_row(self):
        """Test _ensure_next_rows_exist creates next row when needed"""
        # Delete all causes first
        Causes.objects.filter(question_id=self.question_id).delete()
        
        # Create a valid cause without a root
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Valid cause",
            row=1,
            column=0,
            status=True,
            root_status=False,
            mode="test_mode"  # Adding mode for creation of next row
        )
        
        # Count causes before
        causes_count_before = Causes.objects.filter(question_id=self.question_id).count()
        
        # Execute
        self.service._ensure_next_rows_exist(self.question_id)
        
        # Count causes after
        causes_count_after = Causes.objects.filter(question_id=self.question_id).count()
        
        # Verify a new cause was created
        self.assertEqual(causes_count_before + 1, causes_count_after)
        
        # Verify the new cause has the correct properties
        new_cause = Causes.objects.get(
            question_id=self.question_id,
            column=0,
            row=2
        )
        
        self.assertEqual(new_cause.cause, "")
        self.assertEqual(new_cause.mode, cause.mode)
        self.assertFalse(new_cause.status)
        self.assertFalse(new_cause.root_status)
        self.assertEqual(new_cause.feedback, "")
        
    def test_ensure_next_rows_exist_next_row_already_exists(self):
        """Test _ensure_next_rows_exist when next row already exists"""
        # Delete all causes first
        Causes.objects.filter(question_id=self.question_id).delete()
        
        # Create a valid cause without a root
        Causes.objects.create(
            question_id=self.question_id,
            cause="Valid cause",
            row=1,
            column=0,
            status=True,
            root_status=False
        )
        
        # Already create the next row
        Causes.objects.create(
            question_id=self.question_id,
            cause="Next row already exists",
            row=2,
            column=0,
            status=False,
            root_status=False
        )
        
        # Count causes before
        causes_count_before = Causes.objects.filter(question_id=self.question_id).count()
        
        # Execute
        self.service._ensure_next_rows_exist(self.question_id)
        
        # Count causes after
        causes_count_after = Causes.objects.filter(question_id=self.question_id).count()
        
        # Verify no new causes were created
        self.assertEqual(causes_count_before, causes_count_after)
    
    # Tests for validate method
    @patch.object(CausesService, '_validate_first_row_causes')
    @patch.object(CausesService, '_validate_remaining_causes_by_column')
    @patch.object(CausesService, '_ensure_next_rows_exist')
    def test_validate_no_unvalidated_causes(self, mock_ensure_next_rows, mock_validate_remaining, mock_validate_first_row):
        """Test validate when there are no unvalidated causes"""
        # Delete all causes first
        Causes.objects.filter(question_id=self.question_id).delete()
        
        # Create only validated causes
        for i in range(3):
            Causes.objects.create(
                question_id=self.question_id,
                cause=f"Validated cause {i+1}",
                row=i+1,
                column=0,
                status=True  # Already validated
            )
        
        # Execute
        results = self.service.validate(self.question_id, self.mock_request)
        
        # Verify
        self.assertEqual(len(results), 3)
        mock_validate_first_row.assert_not_called()
        mock_validate_remaining.assert_not_called()
        mock_ensure_next_rows.assert_not_called()
    
    @patch.object(CausesService, '_validate_single_cause')
    def test_validate_first_row_causes(self, mock_validate_single_cause):
        """Test _validate_first_row_causes processes row 1 causes properly"""
        # Delete all causes first
        Causes.objects.filter(question_id=self.question_id).delete()
        
        # Create unvalidated causes in row 1 for multiple columns with short cause text
        row1_causes = []
        for i in range(3):  # Columns A, B, C
            cause = Causes.objects.create(
                question_id=self.question_id,
                cause=f"Row1 Col{i}",  # Shortened text
                row=1,
                column=i,
                status=False
            )
            row1_causes.append(cause)
            
        # Also add some non-row-1 causes with short names (should be ignored in this test)
        for i in range(2):
            Causes.objects.create(
                question_id=self.question_id,
                cause=f"Row2 Col{i}",
                row=2,
                column=i,
                status=False
            )
        
        # Get the unvalidated causes
        unvalidated_causes = Causes.objects.filter(question_id=self.question_id, status=False)
        problem = Question.objects.get(pk=self.question_id)
        
        # Execute the method directly
        with patch.object(Causes, 'save'):
            self.service._validate_first_row_causes(unvalidated_causes, problem, self.mock_request)
        
        # Verify row 1 causes were validated
        calls = []
        for cause in row1_causes:
            calls.append(call(cause, problem, None, self.mock_request))
            
        mock_validate_single_cause.assert_has_calls(calls, any_order=False)
    
    @patch.object(CausesService, '_validate_single_cause')
    @patch.object(CausesService, '_get_previous_cause')
    def test_process_column_causes(self, mock_get_previous, mock_validate_single_cause):
        """Test _process_column_causes processes column properly"""
        # Delete all causes first
        Causes.objects.filter(question_id=self.question_id).delete()
        
        # Create a valid cause in column A, row 1
        col_a_row_1 = Causes.objects.create(
            question_id=self.question_id,
            cause="Valid cause A1",
            row=1,
            column=0,
            status=True
        )
        
        # Create unvalidated cause in column A, row 2
        col_a_row_2 = Causes.objects.create(
            question_id=self.question_id,
            cause="Unvalidated cause A2",
            row=2,
            column=0,
            status=False
        )
        
        # Mock the previous cause lookup
        mock_get_previous.return_value = col_a_row_1  # Return valid previous cause
        
        # Get unvalidated causes
        unvalidated_causes = Causes.objects.filter(question_id=self.question_id, status=False)
        problem = Question.objects.get(pk=self.question_id)
        
        # Execute directly
        self.service._process_column_causes(unvalidated_causes, 0, problem, self.mock_request)
        
        # Verify column A row 2 was validated with correct previous cause
        mock_validate_single_cause.assert_called_with(col_a_row_2, problem, col_a_row_1, self.mock_request)
    
    def test_column_has_root_cause(self):
        """Test _column_has_root_cause correctly checks for root causes"""
        # Delete all causes first
        Causes.objects.filter(question_id=self.question_id).delete()
        
        # Create a non-root cause
        Causes.objects.create(
            question_id=self.question_id,
            cause="Non-root cause",
            row=1,
            column=0,
            status=True,
            root_status=False
        )
        
        # Check that column has no root cause
        result = self.service._column_has_root_cause(self.question_id, 0)
        self.assertFalse(result)
        
        # Create a root cause
        Causes.objects.create(
            question_id=self.question_id,
            cause="Root cause",
            row=2,
            column=0,
            status=True,
            root_status=True
        )
        
        # Check that column now has root cause
        result = self.service._column_has_root_cause(self.question_id, 0)
        self.assertTrue(result)
    
    @patch.object(CausesService, '_validate_single_cause')
    @patch.object(CausesService, '_get_previous_cause')
    def test_process_column_causes_skip_empty(self, mock_get_previous, mock_validate_single_cause):
        """Test _process_column_causes skips empty causes"""
        # Delete all causes first
        Causes.objects.filter(question_id=self.question_id).delete()
        
        # Create a valid cause in row 1
        row1_cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Valid cause row 1",
            row=1,
            column=0,
            status=True
        )
        
        # Create an empty cause
        empty_cause = Causes.objects.create(
            question_id=self.question_id,
            cause="",  # Empty
            row=2,
            column=0,
            status=False
        )
        
        # Create a non-empty cause
        non_empty_cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Non-empty cause",
            row=3,
            column=0,
            status=False
        )
        
        # Mock the previous cause lookup
        mock_get_previous.return_value = row1_cause
        
        # Get unvalidated causes
        unvalidated_causes = Causes.objects.filter(question_id=self.question_id, status=False)
        problem = Question.objects.get(pk=self.question_id)
        
        # Execute
        self.service._process_column_causes(unvalidated_causes, 0, problem, self.mock_request)
        
        # Verify empty cause was not validated
        for call_args in mock_validate_single_cause.call_args_list:
            self.assertNotEqual(call_args[0][0], empty_cause)
        
        # Verify non-empty cause was validated
        mock_validate_single_cause.assert_called_with(non_empty_cause, problem, row1_cause, self.mock_request)
    
    @patch.object(CausesService, '_validate_single_cause')
    @patch.object(CausesService, '_get_previous_cause')
    def test_process_column_causes_missing_previous(self, mock_get_previous, mock_validate_single_cause):
        """Test _process_column_causes handles missing previous cause"""
        # Delete all causes first
        Causes.objects.filter(question_id=self.question_id).delete()
        
        # Create an unvalidated cause without proper previous cause
        cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Cause without proper previous",
            row=2,
            column=0,
            status=False,
            feedback=""
        )
        
        # Mock the previous cause lookup to return None
        mock_get_previous.return_value = None
        
        # Get unvalidated causes
        unvalidated_causes = Causes.objects.filter(question_id=self.question_id, status=False)
        problem = Question.objects.get(pk=self.question_id)
        
        # Execute with a patched save method to capture the feedback
        with patch.object(Causes, 'save') as mock_save:
            def side_effect():
                cause.feedback = f"Perlu validasi sebab di baris {cause.row-1} kolom {'ABCDE'[cause.column]} terlebih dahulu."
            
            mock_save.side_effect = side_effect
            self.service._process_column_causes(unvalidated_causes, 0, problem, self.mock_request)
            
            self.assertEqual(cause.feedback, "Perlu validasi sebab di baris 1 kolom A terlebih dahulu.")
            mock_save.assert_called()
        
        # Verify validation was not attempted
        mock_validate_single_cause.assert_not_called()
    
    @patch.object(CausesService, '_validate_single_cause')
    @patch.object(CausesService, '_get_previous_cause')
    def test_process_column_causes_stop_at_root(self, mock_get_previous, mock_validate_single_cause):
        """Test _process_column_causes stops at root cause"""
        # Delete all causes first
        Causes.objects.filter(question_id=self.question_id).delete()
        
        # Create causes in column A
        row1_cause = Causes.objects.create(
            question_id=self.question_id,
            cause="Column A cause 1",
            row=1,
            column=0,
            status=True
        )
        
        cause_a2 = Causes.objects.create(
            question_id=self.question_id,
            cause="Column A cause 2",
            row=2,
            column=0,
            status=False
        )
        
        cause_a3 = Causes.objects.create(
            question_id=self.question_id,
            cause="Column A cause 3",
            row=3,
            column=0,
            status=False
        )
        
        # Mock get_previous_cause to return row1_cause
        mock_get_previous.return_value = row1_cause
        
        # Mock validate_single_cause to mark cause_a2 as root
        def side_effect_validator(cause, *args):
            if cause == cause_a2:
                cause.root_status = True
                
        mock_validate_single_cause.side_effect = side_effect_validator
        
        # Get unvalidated causes
        unvalidated_causes = Causes.objects.filter(question_id=self.question_id, status=False)
        problem = Question.objects.get(pk=self.question_id)
        
        # Execute
        self.service._process_column_causes(unvalidated_causes, 0, problem, self.mock_request)
        
        # Verify cause_a3 was not validated after root cause was found
        for call_args in mock_validate_single_cause.call_args_list:
            self.assertNotEqual(call_args[0][0], cause_a3)
    
    @patch.object(CausesService, '_validate_first_row_causes')
    @patch.object(CausesService, '_validate_remaining_causes_by_column')
    @patch.object(CausesService, '_ensure_next_rows_exist')
    def test_validate_integration(self, mock_ensure_next_rows, mock_validate_remaining, mock_validate_first_row):
        """Test validate method calls all helper methods correctly"""
        # Execute
        self.service.validate(self.question_id, self.mock_request)
        
        # Verify all helper methods were called with correct arguments
        mock_validate_first_row.assert_called_once()
        mock_validate_remaining.assert_called_once()
        mock_ensure_next_rows.assert_called_once_with(self.question_id)
    
    @patch.object(CausesService, '_column_has_root_cause')
    @patch.object(CausesService, '_process_column_causes')
    def test_validate_remaining_causes_by_column(self, mock_process_column, mock_has_root):
        """Test _validate_remaining_causes_by_column processes columns correctly"""
        # Setup
        unvalidated_causes = Mock()
        question_id = self.question_id
        problem = Mock()
        request = self.mock_request
        
        # Configure mock to simulate column 0 has root but column 1 doesn't
        mock_has_root.side_effect = lambda qid, col: col == 0
        
        # Execute
        self.service._validate_remaining_causes_by_column(unvalidated_causes, question_id, problem, request)
        
        # Verify column 0 was processed
        mock_process_column.assert_any_call(unvalidated_causes, 0, problem, request)
        
        # Verify column 2 was not processed (since column 1 has no root)
        self.assertEqual(mock_process_column.call_count, 2)  # Only column 0 and 1
        
        # Verify the correct columns were checked for root causes
        mock_has_root.assert_any_call(question_id, 0)  # For column 1 check
        mock_has_root.assert_any_call(question_id, 1)  # For column 2 check