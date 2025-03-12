from typing import List
from .models import Question
from tag.models import Tag
from validator.exceptions import UniqueTagException
from validator.constants import ErrorMsg


class QuestionService():
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