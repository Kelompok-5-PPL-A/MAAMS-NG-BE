import uuid
from django.test import TestCase, TransactionTestCase
from unittest.mock import patch, Mock, call
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
        self.assertEqual(cause.feedback, f"Sebab di kolom B baris 3 perlu diperbaiki.")
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

    # def test_check_root_cause_true(self):
    #     """Test checking for root cause - true case"""
    #     # Use separate patches to isolate the api_call for root check vs categorize_corruption
    #     with patch.object(CausesService, 'api_call', return_value=1) as mock_api_call:
    #         with patch.object(CausesService, 'categorize_corruption') as mock_categorize:
    #             # Test data
    #             cause = Causes.objects.create(
    #                 question_id=self.question_id,
    #                 cause="This is a root cause",
    #                 row=3,
    #                 column=0,
    #                 status=True
    #             )
                
    #             # Execute
    #             self.service.check_root_cause(cause, self.question, self.mock_request)
                
    #             # Verify
    #             cause.refresh_from_db()
    #             self.assertTrue(cause.root_status)
                
    #             # Verify root check API call
    #             self.assertEqual(mock_api_call.call_count, 1)
                
    #             # Verify categorize_corruption was called
    #             mock_categorize.assert_called_once_with(cause)

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