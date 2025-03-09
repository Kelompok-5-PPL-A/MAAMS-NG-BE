from django.conf import settings
from groq import Groq
import requests
from validator.constants import ErrorMsg, FeedbackMsg
from validator.dataclasses.create_cause import CreateCauseDataClass
from validator.enums import ValidationType
from validator.models import questions
from validator.models.causes import Causes
from validator.services import questions
from validator.exceptions import AIServiceErrorException
import uuid

class CausesService:
    def api_call(self, system_message: str, user_prompt: str, validation_type:ValidationType) -> int:
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
                model="llama-3.3-70b-specdec",
                temperature=0.1,
                max_tokens=50,
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
            
    def retrieve_feedback(self, cause: Causes, problem: questions.Question, prev_cause: None|Causes):
        system_message = "You are a helpful assistant that evaluates causes."
        user_prompt = f"Problem: {problem.question}\nCause: {cause.cause}"
        
        if prev_cause:
            user_prompt += f"\nPrevious cause: {prev_cause.cause}"
   
        result = self.api_call(system_message, user_prompt, ValidationType.FALSE)
        column_letter = chr(65 + cause.column)

        if result == 1:  # Not a cause
            if cause.row == 1:
                cause.feedback = FeedbackMsg.FALSE_ROW_1_NOT_CAUSE.format(column=column_letter)
            else:
                cause.feedback = FeedbackMsg.FALSE_ROW_N_NOT_CAUSE.format(
                    column=column_letter, 
                    row=cause.row, 
                    prev_row=prev_cause.row if prev_cause else cause.row-1
                )
        elif result == 2:  # Positive/Neutral cause
            cause.feedback = FeedbackMsg.FALSE_ROW_N_POSITIVE_NEUTRAL.format(
                column=column_letter, 
                row=cause.row
            )
        elif result == 3:  # Similar to previous
            cause.feedback = FeedbackMsg.FALSE_ROW_N_SIMILAR_PREVIOUS.format(
                column=column_letter, 
                row=cause.row
            )
        
        return cause
        
    def create(self, question_id: uuid, cause: str, row: int, column: int, mode: str) -> CreateCauseDataClass:
        cause = Causes.objects.create(
            problem=questions.Question.objects.get(pk=question_id),
            row=row,
            column=column,
            mode=mode,
            cause=cause
        )
        return CreateCauseDataClass(
            question_id=cause.problem.id,
            id=cause.id,
            row=cause.row,
            column=cause.column,
            mode=cause.mode,
            cause=cause.cause,
            status=cause.status,
            root_status=cause.root_status,
            feedback = cause.feedback
        )