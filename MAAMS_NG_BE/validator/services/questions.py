from typing import List
import uuid
from datetime import (
    datetime, timedelta
)
from multiprocessing.managers import BaseManager
from authentication.models import CustomUser
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from validator.dataclasses.field_values import FieldValuesDataClass
from validator.dataclasses.create_question import CreateQuestionDataClass 

from validator.models.causes import Causes
from validator.models.questions import Question
from validator.models.tag import Tag


class QuestionService():
    def create(self, user: CustomUser | None, title: str, question: str, mode: str, tags: List[str]):
        tags_object = self._validate_tags(tags)

        question_object = Question.objects.create(
            user=user if user else None,  # Jika guest, user None
            title=title,
            question=question,
            mode=mode
        )

        for tag in tags_object:
            question_object.tags.add(tag)

        response = self._make_question_response([question_object])
        return response[0]
