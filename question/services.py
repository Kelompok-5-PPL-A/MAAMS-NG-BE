import uuid
from typing import List, Optional
from .models import Question
from tag.models import Tag
from validator.exceptions import UniqueTagException, ForbiddenRequestException, InvalidFiltersException
from validator.constants import ErrorMsg
from validator.enums import FilterType
from django.core.exceptions import ObjectDoesNotExist
from validator.exceptions import NotFoundRequestException
from .dataclasses.create_question import CreateQuestionDataClass 
from authentication.models import CustomUser
from django.db.models import Q

class QuestionService():
    def create(self, title: str, question: str, mode: str, tags: List[str], user: Optional[CustomUser] = None): 
        tags_object = self._validate_tags(tags)

        question_object = Question.objects.create(
            title=title,
            question=question,
            mode=mode,
            user=user,
        )

        for tag in tags_object:
            question_object.tags.add(tag)

        return question_object
    
    def get(self, pk:uuid):
        try:
            question_object = Question.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise NotFoundRequestException(ErrorMsg.NOT_FOUND)
        return question_object
        
    def get_recent(self, user=None):
        if not user or not user.is_authenticated:
            return None
            
        try:
            recent_question = Question.objects.filter(user=user).order_by('-created_at').first()
            if not recent_question:
                raise Question.DoesNotExist("No recent questions found for this user.")
            return recent_question
        except Exception:
            raise Question.DoesNotExist("No recent questions found.")

    def delete(self, pk):
        """
        Delete a question by its primary key.
        """
        question = Question.objects.get(pk=pk)
        question.delete()

    def _make_question_response(self, questions) -> list:
        response = []
        if len(questions) == 0:
            return response
        for question in questions:
            tags = [tag.name for tag in question.tags.all()]
            
            # Handle the username field for CreateQuestionDataClass
            username = None
            if question.user:
                username = question.user.username
                
            item = CreateQuestionDataClass(
                id=question.id,
                title=question.title,
                question=question.question,
                created_at=question.created_at,
                mode=question.mode,
                tags=tags,
                username=username
            )
            response.append(item)
            
        return response
    
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
    
    def get_privileged(self, q_filter: str, user: CustomUser, keyword: str):
        """
        Return a list of pengawasan questions by keyword and filter type for privileged users.
        """
        # hanya boleh diakses oleh admin (staff dan superuser)
        is_admin = user.is_superuser and user.is_staff
        if not is_admin:
            raise ForbiddenRequestException(ErrorMsg.FORBIDDEN_GET)
        
        if not q_filter:
            q_filter = 'semua'
        if not keyword:
            keyword = ''

        clause = self._resolve_filter_type(q_filter, keyword, is_admin)

        # hanya ambil pertanyaan mode PENGAWASAN + klausa filter lainnya
        mode = Q(mode=Question.ModeChoices.PENGAWASAN)
        questions = Question.objects.filter(mode & clause).order_by('-created_at').distinct()

        return questions

    def _resolve_filter_type(self, filter: str, keyword: str, is_admin: bool) -> Q:
        """
        Returns where clause for questions with specified filters/keywords.
        Only allow superusers/admin to filter by user.
        """
        match filter.lower():
            case FilterType.PENGGUNA.value:
                clause = (Q(user__username__icontains=keyword) | 
                          Q(user__first_name__icontains=keyword) | 
                          Q(user__last_name__icontains=keyword))
            case FilterType.JUDUL.value:
                clause = (Q(title__icontains=keyword) |
                          Q(question__icontains=keyword))
            case FilterType.TOPIK.value:
                clause = Q(tags__name__icontains=keyword)
            case FilterType.SEMUA.value:
                clause = (Q(title__icontains=keyword) |
                          Q(question__icontains=keyword) |
                          Q(tags__name__icontains=keyword))
                if is_admin:
                    clause |= Q(user__username__icontains=keyword)
            case _:
                raise InvalidFiltersException(ErrorMsg.INVALID_FILTERS)
        
        return clause