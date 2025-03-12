from django.conf import settings
from groq import Groq
import requests
from validator.constants import ErrorMsg, FeedbackMsg
from validator.dataclasses.create_cause import CreateCauseDataClass
from validator.enums import ValidationType
from question.models import Question
from validator.models.causes import Causes
from question.services import QuestionService
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
            
    def retrieve_feedback(self, cause: Causes, problem: Question, prev_cause: None|Causes):
        retrieve_feedback_user_prompt = ""
        retrieve_feedback_system_message = ""
        
        if prev_cause:
            retrieve_feedback_user_prompt = (
                f"'{cause.cause}' is the FALSE cause for '{prev_cause.cause}'. "
                "Now determine if it is false because it is NOT THE CAUSE, because it is a POSITIVE OR NEUTRAL cause, or because it is SIMILAR TO THE PREVIOUS cause. "
                "Answer ONLY WITH '1' if it is NOT THE CAUSE,  "
                "ONLY WITH '2' if it is POSITIVE OR NEUTRAL, or "
                "ONLY WITH '3' if it is SIMILAR TO THE PREVIOUS cause."
            )
            retrieve_feedback_system_message = (
                "You are an AI model. You are asked to determine the relationship between the given causes. "
                "Please respond ONLY WITH '1' if the cause is NOT THE CAUSE of the previous cause, "
                "ONLY WITH '2' if the cause is POSITIVE OR NEUTRAL, or "
                "ONLY WITH '3' if the cause is SIMILAR TO THE PREVIOUS cause."
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
        
        feedback_type = CausesService.api_call(self=self, system_message=retrieve_feedback_system_message, user_prompt=retrieve_feedback_user_prompt, validation_type=ValidationType.FALSE)
            
        if feedback_type == 1 and prev_cause:
            cause.feedback = FeedbackMsg.FALSE_ROW_N_NOT_CAUSE.format(column='ABCDE'[cause.column], row=cause.row, prev_row=cause.row-1)
        elif feedback_type == 1:
            cause.feedback = FeedbackMsg.FALSE_ROW_1_NOT_CAUSE.format(column='ABCDE'[cause.column])
        elif feedback_type == 2:
            cause.feedback = FeedbackMsg.FALSE_ROW_N_POSITIVE_NEUTRAL.format(column='ABCDE'[cause.column], row=cause.row)     
        elif feedback_type == 3:
            cause.feedback = FeedbackMsg.FALSE_ROW_N_SIMILAR_PREVIOUS.format(column='ABCDE'[cause.column], row=cause.row) 
        
    def create(self, question_id: uuid, cause: str, row: int, column: int, mode: str) -> CreateCauseDataClass:
        cause = Causes.objects.create(
            problem=Question.objects.get(pk=question_id),
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