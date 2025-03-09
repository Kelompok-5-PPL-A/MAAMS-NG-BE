from django.conf import settings
from groq import Groq
import requests
from validator.constans import ErrorMsg
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