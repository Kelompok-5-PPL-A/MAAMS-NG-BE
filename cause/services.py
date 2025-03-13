from typing import List
from validator.constants import ErrorMsg
from validator.exceptions import ForbiddenRequestException, NotFoundRequestException
from django.core.exceptions import ObjectDoesNotExist
from .dataclasses.create_cause import CreateCauseDataClass
from question.models import Question
from .models import Causes
import uuid

class CausesService:
    def create(self, question_id: uuid, cause: str, row: int, column: int, mode: str) -> CreateCauseDataClass:
        cause = Causes.objects.create(
            question=Question.objects.get(pk=question_id),
            row=row,
            column=column,
            mode=mode,
            cause=cause
        )
        return CreateCauseDataClass(
            question_id=cause.question.id,
            id=cause.id,
            row=cause.row,
            column=cause.column,
            mode=cause.mode,
            cause=cause.cause,
            status=cause.status,
            root_status=cause.root_status,
            feedback = cause.feedback
        )
    

    def get(self, question_id: uuid, pk: uuid) -> CreateCauseDataClass:
        try:
            cause = Causes.objects.get(pk=pk, question_id=question_id)
        except ObjectDoesNotExist:
            raise NotFoundRequestException(ErrorMsg.CAUSE_NOT_FOUND)

        return CreateCauseDataClass(
            question_id=question_id,
            id=cause.id,
            row=cause.row,
            column=cause.column,
            mode=cause.mode,
            cause=cause.cause,
            status=cause.status,
            root_status=cause.root_status,
            feedback = cause.feedback
        )

    def get_list(self, question_id: uuid) -> List[CreateCauseDataClass]:
        try:
            cause = Causes.objects.filter(question_id=question_id)
            current_question = Question.objects.get(pk=question_id)
        except ObjectDoesNotExist:
            raise NotFoundRequestException(ErrorMsg.CAUSE_NOT_FOUND)

        return [
            CreateCauseDataClass(
                question_id=question_id,
                id=cause.id,
                row=cause.row,
                column=cause.column,
                mode=cause.mode,
                cause=cause.cause,
                status=cause.status,
                root_status=cause.root_status,
                feedback = cause.feedback
            )
            for cause in cause
        ]

    def patch_cause(self, question_id: uuid, pk: uuid, cause: str) -> CreateCauseDataClass:
        try:
            causes = Causes.objects.get(question_id=question_id, pk=pk)
            causes.cause = cause
            causes.save()
        except ObjectDoesNotExist:
            raise NotFoundRequestException(ErrorMsg.CAUSE_NOT_FOUND)

        return CreateCauseDataClass(
            question_id=question_id,
            id=causes.id,
            row=causes.row,
            column=causes.column,
            mode=causes.mode,
            cause=causes.cause,
            status=causes.status,
            root_status=causes.root_status,
            feedback = causes.feedback
        )