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
    # User not yet implemented, but it should be none if the role is guest
    def create(self, title: str, question: str, mode: str, tags: List[str]): 
        tags_object = self._validate_tags(tags)

        question_object = Question.objects.create(
            title=title,
            question=question,
            mode=mode
        )

        for tag in tags_object:
            question_object.tags.add(tag)

        return question_object
    
    
    def _validate_tags(self, new_tags: List[str]):
        tags_object = []
        for tag_name in new_tags:
                try:
                    tag = Tag.objects.get(name=tag_name)
                    if tag in tags_object:
                        raise UniqueTagException(ErrorMsg.TAG_MUST_BE_UNIQUE)
                except Tag.DoesNotExist:
                    tag = Tag.objects.create(name=tag_name)
                finally:
                    tags_object.append(tag)
        
        return tags_object