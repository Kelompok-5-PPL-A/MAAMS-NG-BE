import uuid
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

class CausesService:
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
            
    def retrieve_feedback(self, cause: Causes, problem: Question, prev_cause: None|Causes, request):
        retrieve_feedback_user_prompt = ""
        retrieve_feedback_system_message = (
            "You are an AI model analyzing cause-and-effect relationships. When evaluating causes, consider that: "
            "1) Some causes may appear similar to causes in other columns as we get deeper in the analysis "
            "2) Causes should be specific to their parent cause in the same column "
            "3) As analysis progresses, causes often converge toward common root issues "
            "Please respond only with numerical codes as specified in the user prompt."
        )
        
        if prev_cause:
            retrieve_feedback_user_prompt = (
                f"'{cause.cause}' is the FALSE cause for '{prev_cause.cause}'. "
                "Now determine if it is false because it is NOT THE CAUSE, because it is a POSITIVE OR NEUTRAL cause, or because it is SIMILAR TO THE PREVIOUS cause. "
                "Answer ONLY WITH '1' if it is NOT THE CAUSE,  "
                "ONLY WITH '2' if it is POSITIVE OR NEUTRAL, or "
                "ONLY WITH '3' if it is SIMILAR TO THE PREVIOUS cause."
            )   
        else:
            retrieve_feedback_user_prompt = (
                f"'{cause.cause}' is the FALSE cause for this question '{problem.question}'. "
                "Now determine if it is false because it is NOT THE CAUSE or because it is a POSITIVE OR NEUTRAL CAUSE. "
                "Answer ONLY with '1' if it is NOT THE CAUSE, '2' if it is POSITIVE OR NEUTRAL."
            )
            retrieve_feedback_system_message = (
                "You are an AI model. You are asked to determine the relationship between problem and cause. "
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

    def validate(self, question_id: uuid, request):
        unvalidated_causes = Causes.objects.filter(question_id=question_id, status=False)
        
        # If no causes need validation, return empty list
        if not unvalidated_causes.exists():
            return []
        
        problem = Question.objects.get(pk=question_id)
        validated_causes = []
        
        # First validate row 1 across all columns to ensure the foundation is correct
        row1_causes = unvalidated_causes.filter(row=1).order_by('column')
        for cause in row1_causes:
            self._validate_single_cause(cause, problem, None, request)
            validated_causes.append(cause)
        
        # Then proceed column by column, validating completely one column before moving to the next
        for column in range(5):  # Max 5 columns (A-E)
            # Skip if no root cause found in previous column (except for column 0)
            if column > 0:
                previous_column_has_root = Causes.objects.filter(
                    question_id=question_id,
                    column=column-1,
                    root_status=True
                ).exists()
                
                if not previous_column_has_root:
                    continue
            
            # Get all unvalidated causes in this column, ordered by row
            column_causes = unvalidated_causes.filter(
                question_id=question_id,
                column=column,
                row__gt=1  # Exclude row 1 as it's already validated
            ).order_by('row')
            
            # Validate each cause in the column
            for cause in column_causes:
                self._validate_cause(cause, problem, request)
                validated_causes.append(cause)
                
                # If root cause found, break and move to next column
                if cause.root_status:
                    break
        
        return validated_causes
    
    def _validate_cause(self, cause, problem, request):
        # Get the previous cause in the same column
        prev_cause = self._get_previous_cause(cause, problem)
        
        # Skip if previous cause isn't found or isn't valid
        if not prev_cause:
            return
        
        # Validate this cause
        self._validate_single_cause(cause, problem, prev_cause, request)
    
    def _get_previous_cause(self, cause, problem):
        try:
            prev_cause = Causes.objects.filter(
                question_id=problem.pk,
                column=cause.column,
                row=cause.row-1,
                status=True  # Only get validated causes
            ).first()
            
            return prev_cause
        except Causes.DoesNotExist:
            return None
    
    def _validate_single_cause(self, cause, problem, prev_cause, request):
        """Helper method to validate a single cause"""
        if cause.status:
            return
        
        user_prompt = ""
        system_message = (
            "You are an AI model. You are asked to determine whether the given cause is the cause of the given problem. "
            "Consider that as we go deeper in analysis, we're looking for fundamental issues that might relate to: "
            "1) Corruption of wealth (misuse of resources, financial irregularities) "
            "2) Corruption of power (abuse of authority, misuse of position) "
            "3) Corruption of love (favoritism, compromised integrity for relationships) "
            "But at this stage, focus on whether this is a valid cause-effect relationship."
        )
        
        if cause.row == 1:
            user_prompt = f"Is '{cause.cause}' a valid cause of this question: '{problem.question}'? Answer only with True/False"
        else:
            user_prompt = f"Is '{cause.cause}' a valid cause of '{prev_cause.cause}'? Answer only with True/False"
                
        if self.api_call(system_message=system_message, user_prompt=user_prompt, validation_type=ValidationType.NORMAL, request=request) == 1:
            cause.status = True
            cause.feedback = ""
            # Check if this is a root cause (for all valid causes)
            self.check_root_cause(cause=cause, problem=problem, request=request)
        else:
            cause.status = False  # Explicitly set status to False for invalid causes
            self.retrieve_feedback(cause=cause, problem=problem, prev_cause=prev_cause, request=request)
        
        cause.save()
    
    def check_root_cause(self, cause: Causes, problem: Question, request):
        # Enhanced prompt engineering for root cause identification focused on corruption types
        root_check_user_prompt = (
            f"Analyze if the cause '{cause.cause}' is a root cause of '{problem.question}' "
            "that fundamentally relates to one of these corruption types: "
            "1. Korupsi Harta (corruption of wealth) - misuse of resources, funds, assets for personal gain "
            "2. Korupsi Tahta (corruption of power) - abuse of authority, position, or influence "
            "3. Korupsi Cinta (corruption of love) - compromising integrity for personal relationships or emotions "
            "Consider if this cause represents the deepest level of the problem that can be categorized into one of these corruption types. "
            "Answer only with True if this is a root cause that fits one of these categories, or False if it can be analyzed further."
        )
        
        root_check_system_message = (
            "You are an AI model specialized in root cause analysis focusing on corruption patterns. "
            "Your task is to determine whether the given cause is a root cause that fits into one of three corruption categories: "
            "Harta (wealth), Tahta (power), or Cinta (love/relationships). "
            "A root cause is the fundamental underlying issue that, if addressed, would prevent the problem's recurrence. "
            "In this analysis framework, root causes should ultimately connect to one of these corruption types. "
            "Consider if the cause represents: "
            "1) A fundamental issue that can be directly addressed "
            "2) Something that would prevent the problem if eliminated "
            "3) The deepest level that aligns with Harta, Tahta, or Cinta corruption patterns "
            "Focus on whether this cause reaches a level where it clearly represents one of these corruption types. "
            "Respond only with True if this is indeed a root cause aligned with these corruption patterns, or False if it needs further analysis."
        )
        
        if self.api_call(system_message=root_check_system_message, user_prompt=root_check_user_prompt, validation_type=ValidationType.ROOT, request=request) == 1:
            cause.root_status = True
    
            # Enhanced prompt for better categorization of corruption types
            korupsi_check_user_prompt = (
                f"Analyze the root cause '{cause.cause}' in the context of the problem '{problem.question}' "
                "and categorize it into ONE of these corruption types: "
                "\n\n1. Korupsi Harta (corruption of wealth/resources):"
                "\n   - Misappropriation of funds or assets"
                "\n   - Financial irregularities"
                "\n   - Embezzlement or theft of resources"
                "\n   - Using position for personal financial gain"
                "\n   - Manipulating financial systems"
                "\n\n2. Korupsi Tahta (corruption of power/authority):"
                "\n   - Abuse of official position"
                "\n   - Misuse of authority for personal benefit"
                "\n   - Nepotism in appointments or contracts"
                "\n   - Political manipulation"
                "\n   - Bypassing proper procedures using position"
                "\n\n3. Korupsi Cinta (corruption of relationships/emotions):"
                "\n   - Favoritism due to personal relationships"
                "\n   - Compromising integrity for loved ones"
                "\n   - Emotional manipulation in decision-making"
                "\n   - Preferential treatment based on personal connections"
                "\n   - Mixing personal relationships with professional duties"
                "\n\nBased on the root cause and problem context, which category fits best? "
                "Answer ONLY with '1' for Harta, '2' for Tahta, or '3' for Cinta."
            )

            korupsi_check_system_message = (
                "You are an AI model specializing in categorizing corruption types. "
                "Your task is to analyze the root cause and categorize it into one of three corruption types. "
                "Consider the full context of the problem and the nature of the root cause. "
                "Look for patterns that indicate whether the corruption primarily involves: "
                "1) Financial or resource misuse (Harta) "
                "2) Abuse of power or authority (Tahta) "
                "3) Compromised integrity due to relationships (Cinta) "
                "Sometimes a cause may have elements of multiple types, but you must choose the PRIMARY category. "
                "Answer ONLY with '1' for Harta, '2' for Tahta, or '3' for Cinta."
            )
            
            korupsi_category = self.api_call(system_message=korupsi_check_system_message, user_prompt=korupsi_check_user_prompt, validation_type=ValidationType.ROOT_TYPE, request=request)

            if korupsi_category == 1:
                cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Harta."
            elif korupsi_category == 2:
                cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Tahta."
            elif korupsi_category == 3:
                cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Cinta."
            else:
                # Default to Harta if categorization fails
                cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Harta."
            
            cause.save()