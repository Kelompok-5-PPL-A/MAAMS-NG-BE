import uuid
from django.conf import settings
from groq import Groq
import requests
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
    def api_call(self, system_message: str, user_prompt: str, validation_type: ValidationType) -> int:
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
                model="llama-3.1-8b-instant",
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
        
        feedback_type = self.api_call(system_message=retrieve_feedback_system_message, user_prompt=retrieve_feedback_user_prompt, validation_type=ValidationType.FALSE)
            
        if feedback_type == 1 and prev_cause:
            cause.feedback = FeedbackMsg.FALSE_ROW_N_NOT_CAUSE.format(column='ABCDE'[cause.column], row=cause.row, prev_row=cause.row-1)
        elif feedback_type == 1:
            cause.feedback = FeedbackMsg.FALSE_ROW_1_NOT_CAUSE.format(column='ABCDE'[cause.column])
        elif feedback_type == 2:
            cause.feedback = FeedbackMsg.FALSE_ROW_N_POSITIVE_NEUTRAL.format(column='ABCDE'[cause.column], row=cause.row)     
        elif feedback_type == 3:
            cause.feedback = FeedbackMsg.FALSE_ROW_N_SIMILAR_PREVIOUS.format(column='ABCDE'[cause.column], row=cause.row) 

    def validate(self, question_id: uuid):
        max_row = Causes.objects.filter(question_id=question_id).order_by('-row').values_list('row', flat=True).first()
        causes = Causes.objects.filter(question_id=question_id, row=max_row)
        problem = Question.objects.get(pk=question_id)

        for cause in causes:
            if cause.status:
                continue
            
            user_prompt = ""
            prev_cause = None
            system_message = "You are an AI model. You are asked to determine whether the given cause is the cause of the given problem."
            
            if max_row == 1:
                user_prompt = f"Is '{cause.cause}' the cause of this question: '{problem.question}'? Answer only with True/False"
                
            else:
                prev_cause = Causes.objects.filter(question_id=question_id, row=max_row-1, column=cause.column).first()
                user_prompt = f"Is '{cause.cause}' the cause of '{prev_cause.cause}'? Answer only with True/False"
                
            if self.api_call(system_message=system_message, user_prompt=user_prompt, validation_type=ValidationType.NORMAL) == 1:
                cause.status = True
                cause.feedback = ""
                if max_row > 1:
                    self.check_root_cause(cause=cause, problem=problem)

            else:
                self.retrieve_feedback(cause=cause, problem=problem, prev_cause = prev_cause)
            
            cause.save()
    
    def check_root_cause(self, cause: Causes, problem: Question):
        root_check_user_prompt = f"Is the cause '{cause.cause}' the fundamental reason behind the problem '{problem.question}'? Answer only with True or False."
        root_check_system_message = (
            "You are an AI model. You are asked to determine whether the given cause is a root cause of the given problem. "
            "A root cause is the fundamental underlying reason for a problem, which, if addressed, would prevent recurrence of the problem. "
            "Not all direct causes are root causes; while direct causes contribute to the problem, root causes are the deepest level of causation. "
            "Your task is to distinguish between direct causes and root causes, identifying whether the given cause is indeed the fundamental issue driving the problem."
        )
        
        if self.api_call(system_message=root_check_system_message, user_prompt=root_check_user_prompt, validation_type=ValidationType.ROOT) == 1:
            cause.root_status = True
    
            korupsi_check_user_prompt = (
                f"Please categorize the root cause '{cause.cause}' into one of the following corruption categories: "
                "'Harta' (corruption of wealth), 'Tahta' (corruption of power), or 'Cinta' (corruption of love). "
                "Answer ONLY with '1' for Harta, '2' for Tahta, or '3' for Cinta."
            )

            korupsi_check_system_message = (
                "You are an AI model. Your task is to categorize the root cause into one of three corruption categories: "
                "'Harta' for corruption of wealth, 'Tahta' for corruption of power, or 'Cinta' for corruption of love. "
                "You must choose one of these categories, even if the fit seems partial. "
                "Answer ONLY with '1' for Harta, '2' for Tahta, or '3' for Cinta."
            )
            
            korupsi_category = self.api_call(system_message=korupsi_check_system_message, user_prompt=korupsi_check_user_prompt, validation_type=ValidationType.ROOT_TYPE)

            if korupsi_category == 1:
                cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Harta."
            elif korupsi_category == 2:
                cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Tahta."
            elif korupsi_category == 3:
                cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Cinta."
            else:
                cause.feedback = f"{FeedbackMsg.ROOT_FOUND.format(column='ABCDE'[cause.column])} Korupsi Harta."
            
            cause.save()