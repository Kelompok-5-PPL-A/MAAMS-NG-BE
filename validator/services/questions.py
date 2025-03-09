from typing import List
import uuid
from datetime import (
    datetime, timedelta
)
from multiprocessing.managers import BaseManager
#from authentication.models import CustomUser (untuk user jika sudah ada auth)
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from validator.dataclasses.field_values import FieldValuesDataClass
from validator.dataclasses.create_question import CreateQuestionDataClass 

from validator.models.causes import Causes
from validator.models.questions import Question
from validator.models.tag import Tag
from validator.exceptions import UniqueTagException
from validator.constants import ErrorMsg


class QuestionService():
    def create(self, user: None, title: str, question: str, mode: str, tags: List[str]): 

        question_object = Question.objects.create(
            # user=user if user else None,  # Jika guest, user None
            title=title,
            question=question,
            mode=mode
        )

        tag_objects = []
        for tag_name in tags:
            tag_obj, _ = Tag.objects.get_or_create(name=tag_name)  
            tag_objects.append(tag_obj)

        # Add tags to the question
        question_object.tags.set(tag_objects)

        return question_object