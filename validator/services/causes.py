from groq import Groq
from validator.dataclasses.create_cause import CreateCauseDataClass
from validator.models import questions
from validator.models.causes import Causes
from validator.services import questions
from requests.exceptions import RequestException
from validator.exceptions import AIServiceErrorException
import uuid

class CausesService:
    def api_call(self, system_message, user_prompt, validation_type):
        try:
            client = Groq()
            
            messages = [
                {
                    "role": "system",
                    "content": system_message,
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
            
            response = client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-specdec",
                temperature=0.1,
                max_tokens=50,
                seed=42
            )

            content = response.choices[0].message.content.lower()

            if 'true' in content:
                return 1
            else:
                return 0
                
        except RequestException:
            raise AIServiceErrorException("Failed to call the AI service.")
        except Exception as e:
            raise
        
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