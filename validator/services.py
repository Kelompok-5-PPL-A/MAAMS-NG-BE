# import uuid
# import logging
# from django.conf import settings
# from groq import Groq
# import requests
# from django.core.cache import cache
# from validator.constants import ErrorMsg, FeedbackMsg
# from validator.enums import ValidationType
# from question.models import Question
# from cause.models import Causes
# from validator.exceptions import AIServiceErrorException, RateLimitExceededException
# from validator.utils.rate_limiter import RateLimiter
# from googletrans import Translator

# # Set up logging
# logger = logging.getLogger(__name__)

# class CausesService:
#     def __init__(self):
#         self.translator = Translator()
    
#     def translate_to_english(self, text: str) -> str:
#         try:
#             # CRITICAL FIX: Handle async translator correctly
#             translation = self.translator.translate(text, src='id', dest='en')
#             # Make sure we're getting the text from the translation
#             if hasattr(translation, 'text'):
#                 return translation.text
#             # Fallback in case we get a coroutine or other unexpected type
#             return text
#         except Exception as e:
#             logger.error(f"Translation error: {str(e)}")
#             return text
    
#     def api_call(self, system_message: str, user_prompt: str, validation_type:ValidationType, request=None) -> int:
#         client = Groq(api_key=settings.GROQ_API_KEY)
        
#         try:
#             chat_completion = client.chat.completions.create(
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": system_message,
#                     },
#                     {
#                         "role": "user",
#                         "content": user_prompt
#                     }
#                 ],
#                 model="deepseek-r1-distill-llama-70b",
#                 temperature=0.7,
#                 max_completion_tokens=8192,
#                 top_p=0.95,
#                 stream=False,
#                 seed=42
#             )
            
#             answer = chat_completion.choices[0].message.content
#             logger.info(f"API response for {validation_type}: {answer}")
        
#         except requests.exceptions.RequestException as e:
#             logger.error(f"API call error: {str(e)}")
#             raise AIServiceErrorException(ErrorMsg.AI_SERVICE_ERROR)
        
#         if validation_type in [ValidationType.NORMAL, ValidationType.ROOT]:
#             if answer.lower().__contains__('true'):
#                 return 1
#             elif answer.lower().__contains__('false'):
#                 return 0
#         else:
#             if answer.__contains__('1'):
#                 return 1
#             elif answer.__contains__('2'):
#                 return 2
#             elif answer.__contains__('3'):  
#                 return 3
        
#         # Default fallback
#         logger.warning(f"Unexpected response format: {answer}")
#         return 0
    
#     def check_if_corruption_related(self, cause_text: str) -> bool:
#         """Check if the cause text contains corruption-related terms"""
#         corruption_terms = [
#             'korupsi', 'suap', 'sogok', 'pungli', 'pungutan liar',
#             'penyalahgunaan wewenang', 'nepotisme', 'kolusi',
#             'gratifikasi', 'pemalsuan', 'penggelapan', 'penyelewengan',
#             'pemerasan', 'mark up', 'penyimpangan'
#         ]
        
#         # Check in both original and translated text
#         cause_lower = cause_text.lower()
#         cause_en = self.translate_to_english(cause_text).lower()
#         logger.info(f"Checking corruption terms in: {cause_text}")
        
#         corruption_terms_en = [
#             'corruption', 'bribe', 'kickback', 'embezzlement',
#             'abuse of power', 'nepotism', 'collusion', 'fraud',
#             'misappropriation', 'extortion', 'markup', 'misconduct'
#         ]
        
#         # Check if any corruption term exists in the text
#         for term in corruption_terms:
#             if term in cause_lower:
#                 return True
        
#         for term in corruption_terms_en:
#             if term in cause_en:
#                 return True
        
#         return False
            
#     def retrieve_feedback(self, cause: Causes, problem: Question, prev_cause: None|Causes, request):
#         retrieve_feedback_user_prompt = ""
#         retrieve_feedback_system_message = (
#             "You are an AI model analyzing cause-and-effect relationships in a root cause analysis procedure. When evaluating causes, consider that: "
#             "1) Some causes may appear similar to causes in other columns as we get deeper in the analysis "
#             "2) Causes should be specific to their parent cause in the same column, not from other columns "
#             "3) As analysis progresses, causes often converge toward common root issues "
#             "4) Each column represents an independent causal chain that may eventually converge "
#             "5) The 'previous cause' refers to the immediate parent cause in the same column (e.g., A2 is the previous cause for A3)"
#             "Please respond only with numerical codes as specified in the user prompt."
#         )
        
#         # Translate causes to English for better comprehension
#         cause_en = self.translate_to_english(cause.cause)
#         logger.info(f"Analyzing cause: {cause.cause}")
        
#         if prev_cause:
#             prev_cause_en = self.translate_to_english(prev_cause.cause)
#             logger.info(f"Previous cause: {prev_cause.cause}")
#             retrieve_feedback_user_prompt = (
#                 f"'{cause_en}' is the FALSE cause for '{prev_cause_en}' (in column {'ABCDE'[cause.column]}, row {cause.row}, "
#                 f"with previous cause in row {cause.row - 1}). "
#                 "Now determine if it is false because it is NOT THE CAUSE, because it is a POSITIVE OR NEUTRAL cause, or because it is SIMILAR TO THE PREVIOUS cause. "
#                 "Remember that 'previous cause' refers to the cause directly above in the same column, not from other columns. "
#                 "Answer ONLY WITH '1' if it is NOT THE CAUSE,  "
#                 "ONLY WITH '2' if it is POSITIVE OR NEUTRAL, or "
#                 "ONLY WITH '3' if it is SIMILAR TO THE PREVIOUS cause."
#             )   
#         else:
#             problem_en = self.translate_to_english(problem.question)
#             logger.info(f"Problem: {problem.question}")
#             retrieve_feedback_user_prompt = (
#                 f"'{cause_en}' is the FALSE cause for this question '{problem_en}' (in column {'ABCDE'[cause.column]}, first row). "
#                 "Now determine if it is false because it is NOT THE CAUSE or because it is a POSITIVE OR NEUTRAL CAUSE. "
#                 "Answer ONLY with '1' if it is NOT THE CAUSE, '2' if it is POSITIVE OR NEUTRAL."
#             )
#             retrieve_feedback_system_message = (
#                 "You are an AI model analyzing the first level of causes in a root cause analysis. "
#                 "You are asked to determine the relationship between problem and cause. "
#                 "Please respond ONLY WITH '1' if the cause is NOT THE CAUSE of the question, ONLY WITH '2' if the cause is positive or neutral"
#             )
        
#         feedback_type = self.api_call(system_message=retrieve_feedback_system_message, user_prompt=retrieve_feedback_user_prompt, validation_type=ValidationType.FALSE, request=request)
            
#         if feedback_type == 1 and prev_cause:
#             cause.feedback = FeedbackMsg.FALSE_ROW_N_NOT_CAUSE.format(column='ABCDE'[cause.column], row=cause.row, prev_row=cause.row-1)
#         elif feedback_type == 1:
#             cause.feedback = FeedbackMsg.FALSE_ROW_1_NOT_CAUSE.format(column='ABCDE'[cause.column])
#         elif feedback_type == 2:
#             cause.feedback = FeedbackMsg.FALSE_ROW_N_POSITIVE_NEUTRAL.format(column='ABCDE'[cause.column], row=cause.row)     
#         elif feedback_type == 3:
#             cause.feedback = FeedbackMsg.FALSE_ROW_N_SIMILAR_PREVIOUS.format(column='ABCDE'[cause.column], row=cause.row) 
#         else:
#             # Default feedback for unexpected responses
#             cause.feedback = f"Sebab di kolom {'ABCDE'[cause.column]} baris {cause.row} perlu diperbaiki."

#     def validate(self, question_id: uuid, request):
#         """
#         Validate all unvalidated causes for a question.
#         Returns the list of validated causes.
#         """
#         # Get all causes that need validation (all those with status=False)
#         unvalidated_causes = Causes.objects.filter(question_id=question_id, status=False)
        
#         # Log the number of causes to validate
#         logger.info(f"Validating {unvalidated_causes.count()} causes for question {question_id}")
        
#         # CRITICAL FIX: Get all existing causes for this question for reference
#         all_causes = Causes.objects.filter(question_id=question_id)
#         logger.info(f"Total existing causes: {all_causes.count()}")
        
#         # If no causes need validation, return all causes for the question
#         if not unvalidated_causes.exists():
#             return Causes.objects.filter(question_id=question_id).order_by('column', 'row')
        
#         problem = Question.objects.get(pk=question_id)
#         validated_causes = []
        
#         # Log all unvalidated causes for debugging
#         for cause in unvalidated_causes:
#             logger.info(f"Unvalidated cause: column {'ABCDE'[cause.column]}, row {cause.row}, text: '{cause.cause}'")
        
#         # First validate row 1 across all columns to ensure the foundation is correct
#         row1_causes = unvalidated_causes.filter(row=1).order_by('column')
#         for cause in row1_causes:
#             self._validate_single_cause(cause, problem, None, request)
#             validated_causes.append(cause)
        
#         # Then proceed column by column, validating completely one column before moving to the next
#         for column in range(5):  # Max 5 columns (A-E)
#             # For column beyond A, check if previous column has a root cause
#             if column > 0:
#                 previous_column_has_root = Causes.objects.filter(
#                     question_id=question_id,
#                     column=column-1,
#                     root_status=True
#                 ).exists()
                
#                 if not previous_column_has_root:
#                     # Skip this column if previous column doesn't have a root cause
#                     logger.info(f"Skipping column {column} as previous column doesn't have a root cause")
#                     continue
#                 else:
#                     logger.info(f"Processing column {column} since previous column has a root cause")
            
#             # Get all unvalidated causes in this column, ordered by row
#             column_causes = unvalidated_causes.filter(
#                 question_id=question_id,
#                 column=column,
#                 row__gt=1  # Exclude row 1 as it's already validated
#             ).order_by('row')
            
#             # Validate each cause in the column
#             for cause in column_causes:
#                 # Get the previous cause in the same column
#                 prev_cause = self._get_previous_cause(cause, problem)
                
#                 if prev_cause:
#                     logger.info(f"Validating cause in col {'ABCDE'[cause.column]}, row {cause.row} with previous cause: '{prev_cause.cause}'")
#                     self._validate_single_cause(cause, problem, prev_cause, request)
#                 else:
#                     # Log this issue
#                     logger.warning(f"No valid previous cause found for col {'ABCDE'[cause.column]}, row {cause.row}")
#                     cause.feedback = f"Perlu validasi sebab di baris {cause.row-1} kolom {'ABCDE'[cause.column]} terlebih dahulu."
#                     cause.save()
                
#                 validated_causes.append(cause)
                
#                 # If root cause found, stop validating more causes in this column
#                 if cause.root_status:
#                     logger.info(f"Root cause found in column {column}, row {cause.row}")
#                     break
        
#         # CRITICAL FIX: Check for any auto-generated placeholder causes and clean up feedback
#         self._clean_placeholder_feedback(question_id)
        
#         # Create or ensure rows exist for active columns with valid previous rows
#         logger.info("Checking for cases where rows should exist but don't")
#         self._ensure_next_rows_exist(question_id)
        
#         # Return all causes for the question, including newly validated ones
#         all_causes = Causes.objects.filter(question_id=question_id).order_by('column', 'row')
#         logger.info(f"Returning {all_causes.count()} causes total")
#         return all_causes
    
#     def _clean_placeholder_feedback(self, question_id):
#         """
#         Remove placeholder feedback from causes that have user input
#         """
#         placeholder_pattern = "Masukkan sebab dari"
        
#         causes_with_placeholder = Causes.objects.filter(
#             question_id=question_id,
#             feedback__startswith=placeholder_pattern,
#             cause__isnull=False
#         ).exclude(cause="")
        
#         for cause in causes_with_placeholder:
#             logger.info(f"Clearing placeholder feedback for col {'ABCDE'[cause.column]}, row {cause.row}")
#             cause.feedback = ""
#             cause.save()
    
#     def _ensure_next_rows_exist(self, question_id):
#         """
#         Ensure that for each column with a valid row but no root cause,
#         the next row exists for data entry.
#         """
#         # For each active column, find the maximum valid row
#         for column in range(5):  # Columns A-E (0-4)
#             # Skip if the column has a root cause already
#             has_root = Causes.objects.filter(
#                 question_id=question_id,
#                 column=column,
#                 root_status=True
#             ).exists()
            
#             if has_root:
#                 continue
            
#             # Get all valid rows for this column
#             valid_rows = Causes.objects.filter(
#                 question_id=question_id,
#                 column=column,
#                 status=True
#             ).values_list('row', flat=True)
            
#             if not valid_rows.exists():
#                 continue
                
#             max_valid_row = max(valid_rows)
            
#             # Check if next row exists
#             next_row_exists = Causes.objects.filter(
#                 question_id=question_id,
#                 column=column,
#                 row=max_valid_row + 1
#             ).exists()
            
#             # If column has valid rows but no root cause yet, and next row doesn't exist,
#             # create a placeholder for the next row
#             if not next_row_exists:
#                 # Get a cause from the max valid row to use its properties
#                 max_row_cause = Causes.objects.get(
#                     question_id=question_id,
#                     column=column,
#                     row=max_valid_row
#                 )
                
#                 logger.info(f"Creating next row {max_valid_row + 1} for column {'ABCDE'[column]}")
                
#                 # Create a placeholder cause for the next row
#                 Causes.objects.create(
#                     question_id=question_id,
#                     column=column,
#                     row=max_valid_row + 1,
#                     mode=max_row_cause.mode,
#                     cause="",  # Empty cause
#                     status=False,
#                     root_status=False,
#                     feedback=""  # No feedback to avoid confusion
#                 )
    
#     def _get_previous_cause(self, cause, problem):
#         """Get the valid cause from the previous row in the same column."""
#         try:
#             # Get specifically the valid cause from the previous row in the same column
#             prev_cause = Causes.objects.filter(
#                 question_id=problem.pk,
#                 column=cause.column,
#                 row=cause.row-1,
#                 status=True  # Only get validated causes
#             ).first()  # Get the first matching cause if there are multiple
            
#             if prev_cause:
#                 logger.info(f"Found previous cause for column {cause.column}, row {cause.row}: '{prev_cause.cause}'")
#             else:
#                 logger.warning(f"No previous cause found for column {cause.column}, row {cause.row}")
                
#             return prev_cause
#         except Exception as e:
#             logger.error(f"Error finding previous cause: {str(e)}")
#             return None
    
#     def _validate_single_cause(self, cause, problem, prev_cause, request):
#         """Helper method to validate a single cause"""
#         # Skip if already validated with a positive status
#         if cause.status and cause.feedback == "":
#             return
        
#         cause_en = self.translate_to_english(cause.cause)
#         print("Cause in English:", cause_en)
#         problem_en = self.translate_to_english(problem.question)
#         print("Problem in English:", problem_en)
        
#         user_prompt = ""
#         system_message = (
#             "You are an AI model analyzing cause-and-effect relationships in a systematic root cause analysis. "
#             "The analysis follows a column-based approach where each column represents an independent causal chain. "
#             "IMPORTANT PROCEDURAL RULES: "
#             "1) For the first row in each column, the cause must directly relate to the original problem question. "
#             "2) For subsequent rows in the same column, each cause must directly relate to the cause immediately above it (previous row, same column). "
#             "3) The 'previous cause' ALWAYS refers to the cause in the directly preceding row of the same column, not from other columns. "
#             "4) Causal chains may converge as analysis deepens, resulting in similar causes across different columns. "
#             "Please evaluate whether the given cause is valid for its specific position in the analysis."
#         )
        
#         if cause.row == 1:
#             user_prompt = (
#                 f"Is '{cause_en}' the cause of this question: '{problem_en}'? "
#                 f"Note: This is the first row of column {'ABCDE'[cause.column]}. "
#                 "The cause should be a direct response to the main problem. "
#                 "Answer only with True/False"
#             )
#         else:
#             prev_cause_en = self.translate_to_english(prev_cause.cause)
#             print("Previous Cause in English:", prev_cause_en)
#             user_prompt = (
#                 f"Is '{cause_en}' the cause of '{prev_cause_en}'? "
#                 f"Note: This is row {cause.row} of column {'ABCDE'[cause.column]}, and the previous cause is from row {cause.row - 1} of the same column. "
#                 "The cause should be a direct explanation of its immediate parent cause in the same column. "
#                 "Answer only with True/False"
#             )
        
#         # Make the API call to validate this cause
#         validation_result = self.api_call(
#             system_message=system_message, 
#             user_prompt=user_prompt, 
#             validation_type=ValidationType.NORMAL, 
#             request=request
#         )
                
#         if validation_result == 1:
#             # Cause is valid
#             cause.status = True
#             cause.feedback = ""
            
#             # Special check: If this cause mentions corruption and it's a valid cause, it's likely a root cause
#             if self.check_if_corruption_related(cause.cause):
#                 cause.root_status = True
#                 self.categorize_corruption(cause)
#             else:
#                 # Otherwise, check normally if it's a root cause
#                 self.check_root_cause(cause=cause, problem=problem, request=request)
#         else:
#             # Cause is not valid - provide feedback
#             cause.status = False  # Ensure status is explicitly marked as false
#             self.retrieve_feedback(cause=cause, problem=problem, prev_cause=prev_cause, request=request)
        
#         # Save the updated cause
#         cause.save()
    
#     def check_root_cause(self, cause: Causes, problem: Question, request):
#         """Check if a valid cause is a root cause."""
#         cause_en = self.translate_to_english(cause.cause)
#         print("Cause (check root) in English:", cause_en)
#         problem_en = self.translate_to_english(problem.question)
#         print("Problem (check root) in English:", problem_en)
        
#         root_check_user_prompt = (
#             f"Is the cause '{cause_en}' the fundamental reason behind the problem '{problem_en}'? "
#             f"This cause is from column {'ABCDE'[cause.column]}, row {cause.row}. "
#             "Answer only with True or False."
#         )
#         root_check_system_message = (
#             "You are an AI model. You are asked to determine whether the given cause is a root cause of the given problem. "
#             "A root cause is the fundamental underlying reason that, if addressed, would prevent the problem's recurrence. "
#             "In a cause-and-effect chain analysis, a root cause is the deepest level where effective intervention can occur. "
#             "Not all direct causes are root causes. To identify a root cause, consider: "
#             "1) Is this cause something that can be directly addressed? "
#             "2) If this cause were eliminated, would it prevent the problem from recurring? "
#             "3) Is this the most fundamental level of the issue in this causal chain? "
#             "4) For this analysis, root causes often relate to corruption in terms of wealth, power, or love. "
#             "5) If a cause mentions corruption explicitly, it's very likely to be a root cause. "
#             "Respond only with True if this is indeed a root cause, or False if this is an intermediate cause that has deeper underlying causes."
#         )
        
#         if self.api_call(system_message=root_check_system_message, user_prompt=root_check_user_prompt, validation_type=ValidationType.ROOT, request=request) == 1:
#             cause.root_status = True
#             self.categorize_corruption(cause)
    
#     def categorize_corruption(self, cause: Causes):
#         """Helper method to categorize corruption type"""
#         cause_en = self.translate_to_english(cause.cause)
#         print("Cause (categorize corruption) in English:", cause_en)
        
#         korupsi_check_user_prompt = (
#             f"Please categorize the root cause '{cause_en}' into one of the following corruption categories: "
#             "'Harta' (corruption of wealth/money/resources), 'Tahta' (corruption of power/authority/position), or 'Cinta' (corruption of love/relationships/desires). "
#             "IMPORTANT: You MUST choose one of these three categories, even if the fit isn't perfect. "
#             "The root causes should ultimately fall into one of these categories as per the analysis framework. "
#             "Examples: "
#             "- Bribery, embezzlement, or financial misconduct = Harta (1) "
#             "- Abuse of authority, nepotism, or power-seeking = Tahta (2) "
#             "- Personal relationships affecting decisions, favoritism based on personal bonds = Cinta (3) "
#             "Answer ONLY with '1' for Harta, '2' for Tahta, or '3' for Cinta."
#         )

#         korupsi_check_system_message = (
#             "You are an AI model. Your task is to categorize the root cause into one of three corruption categories: "
#             "'Harta' for corruption of wealth, 'Tahta' for corruption of power, or 'Cinta' for corruption of love. "
#             "This is the final step in the root cause analysis framework, where all root causes must be classified "
#             "into one of these three fundamental corruption types. "
#             "You must choose one of these categories, even if the fit seems partial. "
#             "Think broadly about what drives the root cause - is it ultimately about wealth/resources, power/authority, or personal relationships/desires? "
#             "Answer ONLY with '1' for Harta, '2' for Tahta, or '3' for Cinta."
#         )
        
#         korupsi_category = self.api_call(system_message=korupsi_check_system_message, user_prompt=korupsi_check_user_prompt, validation_type=ValidationType.ROOT_TYPE, request=None)

#         if korupsi_category == 1:
#             cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Harta."
#         elif korupsi_category == 2:
#             cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Tahta."
#         elif korupsi_category == 3:
#             cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Cinta."
#         else:
#             # Default to Harta if unclear
#             cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Harta."
        
#         cause.save()

import uuid
import logging
from django.conf import settings
from groq import Groq
import requests
from django.core.cache import cache
from validator.constants import ErrorMsg, FeedbackMsg
from validator.enums import ValidationType
from question.models import Question
from cause.models import Causes
from validator.exceptions import AIServiceErrorException, RateLimitExceededException
from validator.utils.rate_limiter import RateLimiter
from googletrans import Translator

# Set up logging
logger = logging.getLogger(__name__)

class CausesService:
    def __init__(self):
        self.translator = Translator()
    
    def translate_to_english(self, text: str) -> str:
        try:
            # Handle async translator correctly
            translation = self.translator.translate(text, src='id', dest='en')
            # Make sure we're getting the text from the translation
            if hasattr(translation, 'text'):
                return translation.text
            # Fallback in case we get a coroutine or other unexpected type
            return text
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text
    
    def api_call(self, system_message: str, user_prompt: str, validation_type:ValidationType, request=None) -> int:
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
                temperature=0.7,
                max_completion_tokens=8192,
                top_p=0.95,
                stream=False,
                seed=42
            )
            
            answer = chat_completion.choices[0].message.content
            logger.info(f"API response for {validation_type}: {answer}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API call error: {str(e)}")
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
        
        # Default fallback
        logger.warning(f"Unexpected response format: {answer}")
        return 0
    
    def check_if_corruption_related(self, cause_text: str) -> bool:
        """Check if the cause text contains corruption-related terms"""
        corruption_terms = [
            'korupsi', 'suap', 'sogok', 'pungli', 'pungutan liar',
            'penyalahgunaan wewenang', 'nepotisme', 'kolusi',
            'gratifikasi', 'pemalsuan', 'penggelapan', 'penyelewengan',
            'pemerasan', 'mark up', 'penyimpangan'
        ]
        
        # Check in both original and translated text
        cause_lower = cause_text.lower()
        cause_en = self.translate_to_english(cause_text).lower()
        logger.info(f"Checking corruption terms in: {cause_text}")
        
        corruption_terms_en = [
            'corruption', 'bribe', 'kickback', 'embezzlement',
            'abuse of power', 'nepotism', 'collusion', 'fraud',
            'misappropriation', 'extortion', 'markup', 'misconduct'
        ]
        
        # Check if any corruption term exists in the text
        for term in corruption_terms:
            if term in cause_lower:
                return True
        
        for term in corruption_terms_en:
            if term in cause_en:
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
        
        # Translate causes to English for better comprehension
        cause_en = self.translate_to_english(cause.cause)
        logger.info(f"Analyzing cause: {cause.cause}")
        
        if prev_cause:
            prev_cause_en = self.translate_to_english(prev_cause.cause)
            logger.info(f"Previous cause: {prev_cause.cause}")
            retrieve_feedback_user_prompt = (
                f"'{cause_en}' is the FALSE cause for '{prev_cause_en}' (in column {'ABCDE'[cause.column]}, row {cause.row}, "
                f"with previous cause in row {cause.row - 1}). "
                "Now determine if it is false because it is NOT THE CAUSE, because it is a POSITIVE OR NEUTRAL cause, or because it is SIMILAR TO THE PREVIOUS cause. "
                "Remember that 'previous cause' refers to the cause directly above in the same column, not from other columns. "
                "Answer ONLY WITH '1' if it is NOT THE CAUSE,  "
                "ONLY WITH '2' if it is POSITIVE OR NEUTRAL, or "
                "ONLY WITH '3' if it is SIMILAR TO THE PREVIOUS cause."
            )   
        else:
            problem_en = self.translate_to_english(problem.question)
            logger.info(f"Problem: {problem.question}")
            retrieve_feedback_user_prompt = (
                f"'{cause_en}' is the FALSE cause for this question '{problem_en}' (in column {'ABCDE'[cause.column]}, first row). "
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
        
        # Log the number of causes to validate
        logger.info(f"Validating {unvalidated_causes.count()} causes for question {question_id}")
        
        # Get all existing causes for this question for reference
        all_causes = Causes.objects.filter(question_id=question_id)
        logger.info(f"Total existing causes: {all_causes.count()}")
        
        # If no causes need validation, return all causes for the question
        if not unvalidated_causes.exists():
            return Causes.objects.filter(question_id=question_id).order_by('column', 'row')
        
        problem = Question.objects.get(pk=question_id)
        validated_causes = []
        
        # Log all unvalidated causes for debugging
        for cause in unvalidated_causes:
            logger.info(f"Unvalidated cause: column {'ABCDE'[cause.column]}, row {cause.row}, text: '{cause.cause}'")
        
        # First validate row 1 across all columns to ensure the foundation is correct
        row1_causes = unvalidated_causes.filter(row=1).order_by('column')
        for cause in row1_causes:
            self._validate_single_cause(cause, problem, None, request)
            validated_causes.append(cause)
        
        # Then proceed column by column, validating completely one column before moving to the next
        for column in range(5):  # Max 5 columns (A-E)
            # For column beyond A, check if previous column has a root cause
            if column > 0:
                previous_column_has_root = Causes.objects.filter(
                    question_id=question_id,
                    column=column-1,
                    root_status=True
                ).exists()
                
                if not previous_column_has_root:
                    # Skip this column if previous column doesn't have a root cause
                    logger.info(f"Skipping column {column} as previous column doesn't have a root cause")
                    continue
                else:
                    logger.info(f"Processing column {column} since previous column has a root cause")
            
            # Get all unvalidated causes in this column, ordered by row
            column_causes = unvalidated_causes.filter(
                question_id=question_id,
                column=column,
                row__gt=1  # Exclude row 1 as it's already validated
            ).order_by('row')
            
            # Validate each cause in the column
            for cause in column_causes:
                # FIX: Skip empty causes - don't try to validate them
                if not cause.cause or cause.cause.strip() == '':
                    logger.info(f"Skipping empty cause in col {'ABCDE'[cause.column]}, row {cause.row}")
                    continue
                
                # Get the previous cause in the same column
                prev_cause = self._get_previous_cause(cause, problem)
                
                if prev_cause:
                    logger.info(f"Validating cause in col {'ABCDE'[cause.column]}, row {cause.row} with previous cause: '{prev_cause.cause}'")
                    self._validate_single_cause(cause, problem, prev_cause, request)
                else:
                    # Log this issue
                    logger.warning(f"No valid previous cause found for col {'ABCDE'[cause.column]}, row {cause.row}")
                    cause.feedback = f"Perlu validasi sebab di baris {cause.row-1} kolom {'ABCDE'[cause.column]} terlebih dahulu."
                    cause.save()
                
                validated_causes.append(cause)
                
                # If root cause found, stop validating more causes in this column
                if cause.root_status:
                    logger.info(f"Root cause found in column {column}, row {cause.row}")
                    break
        
        # FIX: Clean up any empty feedback from placeholder causes
        self._clean_placeholder_feedback(question_id)
        
        # Create or ensure rows exist for active columns with valid previous rows
        logger.info("Checking for cases where rows should exist but don't")
        self._ensure_next_rows_exist(question_id)
        
        # Return all causes for the question, including newly validated ones
        all_causes = Causes.objects.filter(question_id=question_id).order_by('column', 'row')
        logger.info(f"Returning {all_causes.count()} causes total")
        return all_causes
    
    def _clean_placeholder_feedback(self, question_id):
        """
        Remove placeholder feedback from causes that have user input
        """
        # FIX: Remove placeholder feedback from empty cells and cells with user input
        placeholder_pattern = "Masukkan sebab dari"
        
        # First, find causes with placeholder feedback but with actual user input
        causes_with_placeholder = Causes.objects.filter(
            question_id=question_id,
            feedback__startswith=placeholder_pattern,
            cause__isnull=False
        ).exclude(cause="")
        
        for cause in causes_with_placeholder:
            logger.info(f"Clearing placeholder feedback for col {'ABCDE'[cause.column]}, row {cause.row}")
            cause.feedback = ""
            cause.save()
            
        # FIX: For empty causes, also clear any feedback to prevent showing them before user input
        empty_causes = Causes.objects.filter(
            question_id=question_id,
            cause__exact="",
            status=False,
            root_status=False
        )
        
        for cause in empty_causes:
            if cause.feedback:
                logger.info(f"Clearing feedback from empty cause in col {'ABCDE'[cause.column]}, row {cause.row}")
                cause.feedback = ""
                cause.save()
    
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
                
                logger.info(f"Creating next row {max_valid_row + 1} for column {'ABCDE'[column]}")
                
                # Create a placeholder cause for the next row
                # FIX: Ensure we create empty causes with NO feedback and NOT marked as root
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
            # FIX: Add validation for row number
            if cause.row <= 1:
                logger.warning(f"No previous cause possible for row {cause.row} in column {cause.column}")
                return None
                
            # Get specifically the valid cause from the previous row in the same column
            prev_cause = Causes.objects.filter(
                question_id=problem.pk,
                column=cause.column,
                row=cause.row-1,
                status=True  # Only get validated causes
            ).first()  # Get the first matching cause if there are multiple
            
            if prev_cause:
                # FIX: Check that the previous cause actually has content
                if prev_cause.cause and prev_cause.cause.strip() != "":
                    logger.info(f"Found previous cause for column {cause.column}, row {cause.row}: '{prev_cause.cause}'")
                    return prev_cause
                else:
                    logger.warning(f"Previous cause exists but is empty for column {cause.column}, row {cause.row-1}")
                    return None
            else:
                logger.warning(f"No previous cause found for column {cause.column}, row {cause.row}")
                return None
        except Exception as e:
            logger.error(f"Error finding previous cause: {str(e)}")
            return None
    
    def _validate_single_cause(self, cause, problem, prev_cause, request):
        """Helper method to validate a single cause"""
        # Skip if already validated with a positive status
        if cause.status and cause.feedback == "":
            return
            
        # FIX: Skip empty causes to prevent validating them
        if not cause.cause or cause.cause.strip() == "":
            logger.info(f"Skipping validation for empty cause in col {'ABCDE'[cause.column]}, row {cause.row}")
            return
        
        cause_en = self.translate_to_english(cause.cause)
        print("Cause in English:", cause_en)
        problem_en = self.translate_to_english(problem.question)
        print("Problem in English:", problem_en)
        
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
                f"Is '{cause_en}' the cause of this question: '{problem_en}'? "
                f"Note: This is the first row of column {'ABCDE'[cause.column]}. "
                "The cause should be a direct response to the main problem. "
                "Answer only with True/False"
            )
        else:
            # FIX: Ensure we have a valid previous cause before proceeding
            if not prev_cause or not prev_cause.cause or prev_cause.cause.strip() == "":
                logger.warning(f"No valid previous cause for col {'ABCDE'[cause.column]}, row {cause.row}")
                cause.status = False
                cause.feedback = f"Perlu validasi sebab di baris {cause.row-1} kolom {'ABCDE'[cause.column]} terlebih dahulu."
                cause.save()
                return
                
            prev_cause_en = self.translate_to_english(prev_cause.cause)
            print("Previous Cause in English:", prev_cause_en)
            user_prompt = (
                f"Is '{cause_en}' the cause of '{prev_cause_en}'? "
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
            cause.root_status = False  # FIX: Ensure invalid causes are NOT marked as root causes
            self.retrieve_feedback(cause=cause, problem=problem, prev_cause=prev_cause, request=request)
        
        # Save the updated cause
        cause.save()
    
    def check_root_cause(self, cause: Causes, problem: Question, request):
        """Check if a valid cause is a root cause."""
        # FIX: For empty causes or new cells without user input, skip root cause check
        if not cause.cause or cause.cause.strip() == "":
            logger.info(f"Skipping root cause check for empty cause in col {'ABCDE'[cause.column]}, row {cause.row}")
            cause.root_status = False
            return
            
        # FIX: Add additional check to prevent auto-marking cells as root causes in new columns
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
                logger.info(f"Skipping root cause check for col {'ABCDE'[cause.column]}, row {cause.row} - too early in column")
                cause.root_status = False
                return
        
        cause_en = self.translate_to_english(cause.cause)
        print("Cause (check root) in English:", cause_en)
        problem_en = self.translate_to_english(problem.question)
        print("Problem (check root) in English:", problem_en)
        
        root_check_user_prompt = (
            f"Is the cause '{cause_en}' the fundamental reason behind the problem '{problem_en}'? "
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
        
        # FIX: Add more explicit logging
        logger.info(f"Checking if cause in col {'ABCDE'[cause.column]}, row {cause.row} is a root cause")
        
        if self.api_call(system_message=root_check_system_message, user_prompt=root_check_user_prompt, validation_type=ValidationType.ROOT, request=request) == 1:
            logger.info(f"Root cause FOUND in col {'ABCDE'[cause.column]}, row {cause.row}")
            cause.root_status = True
            self.categorize_corruption(cause)
        else:
            logger.info(f"NOT a root cause in col {'ABCDE'[cause.column]}, row {cause.row}")
            cause.root_status = False
    
    def categorize_corruption(self, cause: Causes):
        """Helper method to categorize corruption type"""
        # FIX: Added validation to prevent categorizing empty causes
        if not cause.cause or cause.cause.strip() == "":
            logger.warning(f"Attempted to categorize empty cause in col {'ABCDE'[cause.column]}, row {cause.row}")
            cause.root_status = False
            cause.feedback = ""
            cause.save()
            return
        
        cause_en = self.translate_to_english(cause.cause)
        print("Cause (categorize corruption) in English:", cause_en)
        
        korupsi_check_user_prompt = (
            f"Please categorize the root cause '{cause_en}' into one of the following corruption categories: "
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
        
        # Log the categorization attempt
        logger.info(f"Categorizing root cause in col {'ABCDE'[cause.column]}, row {cause.row}")
        
        korupsi_category = self.api_call(system_message=korupsi_check_system_message, user_prompt=korupsi_check_user_prompt, validation_type=ValidationType.ROOT_TYPE, request=None)

        if korupsi_category == 1:
            cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Harta."
            logger.info(f"Root cause in col {'ABCDE'[cause.column]}, row {cause.row} categorized as: Harta")
        elif korupsi_category == 2:
            cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Tahta."
            logger.info(f"Root cause in col {'ABCDE'[cause.column]}, row {cause.row} categorized as: Tahta")
        elif korupsi_category == 3:
            cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Cinta."
            logger.info(f"Root cause in col {'ABCDE'[cause.column]}, row {cause.row} categorized as: Cinta")
        else:
            # Default to Harta if unclear
            cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Harta."
            logger.info(f"Root cause in col {'ABCDE'[cause.column]}, row {cause.row} defaulted to: Harta")
        
        cause.save()