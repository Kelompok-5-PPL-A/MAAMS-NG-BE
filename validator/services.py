import uuid
from django.conf import settings
from groq import Groq
import requests
from django.core.cache import cache
from validator.constants import ErrorMsg, FeedbackMsg
from validator.enums import ValidationType
from question.models import Question
from cause.models import Causes
from validator.exceptions import AIServiceErrorException
from arize.otel import register
from openinference.instrumentation.groq import GroqInstrumentor

tracer_provider = register(
    space_id = settings.ARIZE_SPACE_ID,
    api_key = settings.ARIZE_API_KEY,
    project_name = "MAAMS NG"
)
GroqInstrumentor().instrument(tracer_provider=tracer_provider)

class CausesService:
    def api_call(self, system_message: str, user_prompt: str, validation_type: ValidationType, request=None) -> int:
        client = Groq(api_key=settings.GROQ_API_KEY)
        
        try:
            chat_completion = client.chat.completions.create(
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
                temperature=0.6,
                top_p=0.95,
                stream=False,
                seed=42
            )
            
            answer = chat_completion.choices[0].message.content
        
        except requests.exceptions.RequestException:
            raise AIServiceErrorException(ErrorMsg.AI_SERVICE_ERROR)
        
        if validation_type in [ValidationType.NORMAL, ValidationType.ROOT]:
            if answer.lower().__contains__('true'):
                return 1
            elif answer.lower().__contains__('false'):
                return 0
        else:
            if answer.__contains__('1'):
                return 1
            elif answer.__contains__('2'):
                return 2
            elif answer.__contains__('3'):  
                return 3

        return 0
    
    def check_if_corruption_related(self, cause_text: str) -> bool:
        """Check if the cause text contains corruption-related terms"""
        corruption_terms = [
            'korupsi', 'suap', 'sogok', 'pungli', 'pungutan liar',
            'penyalahgunaan wewenang', 'nepotisme', 'kolusi',
            'gratifikasi', 'pemalsuan', 'penggelapan', 'penyelewengan',
            'pemerasan', 'mark up', 'penyimpangan'
        ]

        cause_lower = cause_text.lower()
        
        for term in corruption_terms:
            if term in cause_lower:
                return True
        
        return False
            
    def retrieve_feedback(self, cause: Causes, problem: Question, prev_cause: None|Causes, request):
        retrieve_feedback_user_prompt = ""
        retrieve_feedback_system_message = (
            "You are an AI model analyzing cause-and-effect relationships in a root cause analysis procedure. When evaluating causes, consider that: "
            "1) Some causes may appear similar to causes in other columns as we get deeper in the analysis "
            "2) Causes should be specific to their parent cause in the same column, not from other columns "
            "3) As analysis progresses, causes often converge toward common root issues "
            "4) Each column represents an independent causal chain that may eventually converge "
            "5) The 'previous cause' refers to the immediate parent cause in the same column (e.g., A2 is the previous cause for A3)"
            "Please respond only with numerical codes as specified in the user prompt."
        )
        
        if prev_cause:
            retrieve_feedback_user_prompt = (
                f"'{cause.cause}' is the FALSE cause for '{prev_cause.cause}' (in column {'ABCDE'[cause.column]}, row {cause.row}, "
                f"with previous cause in row {cause.row - 1}). "
                "Now determine if it is false because it is NOT THE CAUSE, because it is a POSITIVE OR NEUTRAL cause, or because it is SIMILAR TO THE PREVIOUS cause. "
                "Remember that 'previous cause' refers to the cause directly above in the same column, not from other columns. "
                "Answer ONLY WITH '1' if it is NOT THE CAUSE,  "
                "ONLY WITH '2' if it is POSITIVE OR NEUTRAL, or "
                "ONLY WITH '3' if it is SIMILAR TO THE PREVIOUS cause."
            )   
        else:
            retrieve_feedback_user_prompt = (
                f"'{cause.cause}' is the FALSE cause for this question '{problem.question}' (in column {'ABCDE'[cause.column]}, first row). "
                "Now determine if it is false because it is NOT THE CAUSE or because it is a POSITIVE OR NEUTRAL CAUSE. "
                "Answer ONLY with '1' if it is NOT THE CAUSE, '2' if it is POSITIVE OR NEUTRAL."
            )
            retrieve_feedback_system_message = (
                "You are an AI model analyzing the first level of causes in a root cause analysis. "
                "You are asked to determine the relationship between problem and cause. "
                "Please respond ONLY WITH '1' if the cause is NOT THE CAUSE of the question, ONLY WITH '2' if the cause is positive or neutral"
            )
        
        feedback_type = self.api_call(system_message=retrieve_feedback_system_message, user_prompt=retrieve_feedback_user_prompt, validation_type=ValidationType.FALSE, request=request)
            
        if feedback_type == 1 and prev_cause:
            cause.feedback = FeedbackMsg.FALSE_ROW_N_NOT_CAUSE.format(column='ABCDE'[cause.column], row=cause.row, prev_row=cause.row-1)
        elif feedback_type == 1:
            cause.feedback = FeedbackMsg.FALSE_ROW_1_NOT_CAUSE.format(column='ABCDE'[cause.column])
        elif feedback_type == 2:
            cause.feedback = FeedbackMsg.FALSE_ROW_N_POSITIVE_NEUTRAL.format(column='ABCDE'[cause.column], row=cause.row)     
        elif feedback_type == 3:
            cause.feedback = FeedbackMsg.FALSE_ROW_N_SIMILAR_PREVIOUS.format(column='ABCDE'[cause.column], row=cause.row) 
        else:
            # Default feedback for unexpected responses
            cause.feedback = f"Sebab di kolom {'ABCDE'[cause.column]} baris {cause.row} perlu diperbaiki."

    def validate(self, question_id: uuid, request):
        """
        Validate all unvalidated causes for a question.
        Returns the list of validated causes.
        """
        # Get all causes that need validation (all those with status=False)
        unvalidated_causes = Causes.objects.filter(question_id=question_id, status=False)
        
        # If no causes need validation, return all causes for the question
        if not unvalidated_causes.exists():
            return Causes.objects.filter(question_id=question_id).order_by('column', 'row')
        
        problem = Question.objects.get(pk=question_id)
        
        # First validate row 1 across all columns
        self._validate_first_row_causes(unvalidated_causes, problem, request)
        
        # Then proceed column by column
        self._validate_remaining_causes_by_column(unvalidated_causes, question_id, problem, request)
        
        # Create or ensure rows exist for active columns with valid previous rows
        self._ensure_next_rows_exist(question_id)
        
        # Return all causes for the question, including newly validated ones
        return Causes.objects.filter(question_id=question_id).order_by('column', 'row')

    def _validate_first_row_causes(self, unvalidated_causes, problem, request):
        """Validate all causes in the first row across all columns."""
        row1_causes = unvalidated_causes.filter(row=1).order_by('column')
        for cause in row1_causes:
            if cause.cause and cause.cause.strip():  # Only validate non-empty causes
                self._validate_single_cause(cause, problem, None, request)

    def _validate_remaining_causes_by_column(self, unvalidated_causes, question_id, problem, request):
        """Validate causes in rows > 1, proceeding column by column."""
        for column in range(5):  # Max 5 columns (A-E)
            # Skip column if previous column doesn't have a root cause (except for column A)
            if column > 0 and not self._column_has_root_cause(question_id, column-1):
                continue
                
            # Process each cause in the current column beyond row 1
            self._process_column_causes(unvalidated_causes, column, problem, request)

    def _column_has_root_cause(self, question_id, column):
        """Check if the specified column has a root cause."""
        return Causes.objects.filter(
            question_id=question_id,
            column=column,
            root_status=True
        ).exists()

    def _process_column_causes(self, unvalidated_causes, column, problem, request):
        """Process all unvalidated causes in a specific column (rows > 1)."""
        column_causes = unvalidated_causes.filter(
            question_id=problem.pk,
            column=column,
            row__gt=1  # Exclude row 1 as it's already validated
        ).order_by('row')
        
        for cause in column_causes:
            # Skip empty causes
            if not cause.cause or cause.cause.strip() == '':
                continue
            
            prev_cause = self._get_previous_cause(cause, problem)
            
            if prev_cause:
                self._validate_single_cause(cause, problem, prev_cause, request)
            else:
                cause.feedback = f"Perlu validasi sebab di baris {cause.row-1} kolom {'ABCDE'[cause.column]} terlebih dahulu."
                cause.save()
            
            # If root cause found, stop validating more causes in this column
            if cause.root_status:
                break
    
    def _ensure_next_rows_exist(self, question_id):
        """
        Ensure that for each column with a valid row but no root cause,
        the next row exists for data entry.
        """
        # For each active column, find the maximum valid row
        for column in range(5):  # Columns A-E (0-4)
            # Skip if the column has a root cause already
            has_root = Causes.objects.filter(
                question_id=question_id,
                column=column,
                root_status=True
            ).exists()
            
            if has_root:
                continue
            
            # Get all valid rows for this column
            valid_rows = Causes.objects.filter(
                question_id=question_id,
                column=column,
                status=True
            ).values_list('row', flat=True)
            
            if not valid_rows.exists():
                continue
                
            max_valid_row = max(valid_rows)
            
            # Check if next row exists
            next_row_exists = Causes.objects.filter(
                question_id=question_id,
                column=column,
                row=max_valid_row + 1
            ).exists()
            
            # If column has valid rows but no root cause yet, and next row doesn't exist,
            # create a placeholder for the next row
            if not next_row_exists:
                # Get a cause from the max valid row to use its properties
                max_row_cause = Causes.objects.get(
                    question_id=question_id,
                    column=column,
                    row=max_valid_row
                )
                
                # Create a placeholder cause for the next row
                # Ensure we create empty causes with NO feedback and NOT marked as root
                Causes.objects.create(
                    question_id=question_id,
                    column=column,
                    row=max_valid_row + 1,
                    mode=max_row_cause.mode,
                    cause="",  # Empty cause
                    status=False,
                    root_status=False,  # Explicitly NOT a root cause
                    feedback=""  # No feedback to avoid confusion
                )
    
    def _get_previous_cause(self, cause, problem):
        """Get the valid cause from the previous row in the same column."""
        try:
            # Add validation for row number
            if cause.row <= 1:
                return None
                
            # Get specifically the valid cause from the previous row in the same column
            prev_cause = Causes.objects.filter(
                question_id=problem.pk,
                column=cause.column,
                row=cause.row-1,
                status=True  # Only get validated causes
            ).first()  # Get the first matching cause if there are multiple
            
            if prev_cause:
                # Check that the previous cause actually has content
                if prev_cause.cause and prev_cause.cause.strip() != "":
                    return prev_cause
                else:
                    return None
            else:
                return None
        except Exception:
            return None
    
    def _validate_single_cause(self, cause, problem, prev_cause, request):
        """Helper method to validate a single cause"""
        # Skip if already validated with a positive status
        if cause.status and cause.feedback == "":
            return
            
        # Skip empty causes to prevent validating them
        if not cause.cause or cause.cause.strip() == "":
            return
        
        user_prompt = ""
        system_message = (
            "You are an AI model analyzing cause-and-effect relationships in a systematic root cause analysis. "
            "The analysis follows a column-based approach where each column represents an independent causal chain. "
            "IMPORTANT PROCEDURAL RULES: "
            "1) For the first row in each column, the cause must directly relate to the original problem question. "
            "2) For subsequent rows in the same column, each cause must directly relate to the cause immediately above it (previous row, same column). "
            "3) The 'previous cause' ALWAYS refers to the cause in the directly preceding row of the same column, not from other columns. "
            "4) Causal chains may converge as analysis deepens, resulting in similar causes across different columns. "
            "Please evaluate whether the given cause is valid for its specific position in the analysis."
        )
        
        if cause.row == 1:
            user_prompt = (
                f"Is '{cause.cause}' the cause of this question: '{problem.question}'? "
                f"Note: This is the first row of column {'ABCDE'[cause.column]}. "
                "The cause should be a direct response to the main problem. "
                "Answer only with True/False"
            )
        else:
            # Ensure we have a valid previous cause before proceeding
            if not prev_cause or not prev_cause.cause or prev_cause.cause.strip() == "":
                cause.status = False
                cause.feedback = f"Perlu validasi sebab di baris {cause.row-1} kolom {'ABCDE'[cause.column]} terlebih dahulu."
                cause.save()
                return
                
            user_prompt = (
                f"Is '{cause.cause}' the cause of '{prev_cause.cause}'? "
                f"Note: This is row {cause.row} of column {'ABCDE'[cause.column]}, and the previous cause is from row {cause.row - 1} of the same column. "
                "The cause should be a direct explanation of its immediate parent cause in the same column. "
                "Answer only with True/False"
            )
        
        # Make the API call to validate this cause
        validation_result = self.api_call(
            system_message=system_message, 
            user_prompt=user_prompt, 
            validation_type=ValidationType.NORMAL, 
            request=request
        )
                
        if validation_result == 1:
            # Cause is valid
            cause.status = True
            cause.feedback = ""
            
            # Special check: If this cause mentions corruption and it's a valid cause, it's likely a root cause
            if self.check_if_corruption_related(cause.cause):
                cause.root_status = True
                self.categorize_corruption(cause)
            else:
                # Otherwise, check normally if it's a root cause
                self.check_root_cause(cause=cause, problem=problem, request=request)
        else:
            # Cause is not valid - provide feedback
            cause.status = False  # Ensure status is explicitly marked as false
            cause.root_status = False  # Ensure invalid causes are NOT marked as root causes
            self.retrieve_feedback(cause=cause, problem=problem, prev_cause=prev_cause, request=request)
        
        # Save the updated cause
        cause.save()
    
    def check_root_cause(self, cause: Causes, problem: Question, request):
        """Check if a valid cause is a root cause."""
        # For empty causes or new cells without user input, skip root cause check
        if not cause.cause or cause.cause.strip() == "":
            cause.root_status = False
            return
            
        # Add additional check to prevent auto-marking cells as root causes in new columns
        # For rows > 1 in columns C-E, don't automatically check for root cause in initial cells
        if cause.column >= 2 and cause.row > 1:
            # Check how many causes exist in this column
            column_causes_count = Causes.objects.filter(
                question_id=problem.pk,
                column=cause.column,
                status=True
            ).count()
            
            # For newly activated columns with just 1-2 validated causes, skip root check
            # This prevents premature root cause detection in new columns
            if column_causes_count <= 2:
                cause.root_status = False
                return
        
        root_check_user_prompt = (
            f"Is the cause '{cause.cause}' the fundamental reason behind the problem '{problem.question}'? "
            f"This cause is from column {'ABCDE'[cause.column]}, row {cause.row}. "
            "Answer only with True or False."
        )
        root_check_system_message = (
            "You are an AI model. You are asked to determine whether the given cause is a root cause of the given problem. "
            "A root cause is the fundamental underlying reason that, if addressed, would prevent the problem's recurrence. "
            "In a cause-and-effect chain analysis, a root cause is the deepest level where effective intervention can occur. "
            "Not all direct causes are root causes. To identify a root cause, consider: "
            "1) Is this cause something that can be directly addressed? "
            "2) If this cause were eliminated, would it prevent the problem from recurring? "
            "3) Is this the most fundamental level of the issue in this causal chain? "
            "4) For this analysis, root causes often relate to corruption in terms of wealth, power, or love. "
            "5) If a cause mentions corruption explicitly, it's very likely to be a root cause. "
            "Respond only with True if this is indeed a root cause, or False if this is an intermediate cause that has deeper underlying causes."
        )
        
        if self.api_call(system_message=root_check_system_message, user_prompt=root_check_user_prompt, validation_type=ValidationType.ROOT, request=request) == 1:
            cause.root_status = True
            self.categorize_corruption(cause)
        else:
            cause.root_status = False
    
    def categorize_corruption(self, cause: Causes):
        """Helper method to categorize corruption type"""
        # Added validation to prevent categorizing empty causes
        if not cause.cause or cause.cause.strip() == "":
            cause.root_status = False
            cause.feedback = ""
            cause.save()
            return
        
        korupsi_check_user_prompt = (
            f"Please categorize the root cause '{cause.cause}' into one of the following corruption categories: "
            "'Harta' (corruption of wealth/money/resources), 'Tahta' (corruption of power/authority/position), or 'Cinta' (corruption of love/relationships/desires). "
            "IMPORTANT: You MUST choose one of these three categories, even if the fit isn't perfect. "
            "The root causes should ultimately fall into one of these categories as per the analysis framework. "
            "Examples: "
            "- Bribery, embezzlement, or financial misconduct = Harta (1) "
            "- Abuse of authority, nepotism, or power-seeking = Tahta (2) "
            "- Personal relationships affecting decisions, favoritism based on personal bonds = Cinta (3) "
            "Answer ONLY with '1' for Harta, '2' for Tahta, or '3' for Cinta."
        )

        korupsi_check_system_message = (
            "You are an AI model. Your task is to categorize the root cause into one of three corruption categories: "
            "'Harta' for corruption of wealth, 'Tahta' for corruption of power, or 'Cinta' for corruption of love. "
            "This is the final step in the root cause analysis framework, where all root causes must be classified "
            "into one of these three fundamental corruption types. "
            "You must choose one of these categories, even if the fit seems partial. "
            "Think broadly about what drives the root cause - is it ultimately about wealth/resources, power/authority, or personal relationships/desires? "
            "Answer ONLY with '1' for Harta, '2' for Tahta, or '3' for Cinta."
        )
        
        korupsi_category = self.api_call(system_message=korupsi_check_system_message, user_prompt=korupsi_check_user_prompt, validation_type=ValidationType.ROOT_TYPE, request=None)

        if korupsi_category == 1:
            cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Harta."
        elif korupsi_category == 2:
            cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Tahta."
        elif korupsi_category == 3:
            cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Cinta."
        else:
            # Default to Harta if unclear
            cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Harta."
        
        cause.save()