from rest_framework import serializers
from .models import Question

class BaseQuestion(serializers.Serializer):
    MODE_CHOICES = Question.ModeChoices

    class Meta:
        ref_name = 'BaseQuestion'
        
    mode = serializers.ChoiceField(choices=MODE_CHOICES)
    
class QuestionTitleRequest(serializers.Serializer):
    class Meta:
        ref_name = 'QuestionTitleRequest'
        
    title = serializers.CharField(max_length=40)
    
class QuestionTagRequest(serializers.Serializer):
    class Meta:
        ref_name = 'QuestionTagRequest'
        
    tags = serializers.ListField(
        min_length=1,
        max_length=3,
        child=serializers.CharField(max_length=10))    

class QuestionRequest(BaseQuestion):
    class Meta:
        ref_name = 'QuestionRequest'

    title = serializers.CharField(max_length=40)
    question = serializers.CharField(max_length=255)
    tags = serializers.ListField(
        min_length=1,
        max_length=3,
        child=serializers.CharField(max_length=10))
    
class QuestionResponse(BaseQuestion):
    class Meta:
        ref_name = 'QuestionResponse'
    
    id = serializers.UUIDField()
    title = serializers.CharField(max_length=40)
    question = serializers.CharField(max_length=255)
    created_at = serializers.DateTimeField()
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    user = serializers.SlugRelatedField(read_only=True, slug_field="uuid")
    username = serializers.CharField(source='user.username', read_only=True)
    
class PaginatedQuestionResponse(serializers.Serializer):
    class Meta:
        ref_name = 'QuestionResponsePaginated'

    count = serializers.IntegerField(default=5)
    next = serializers.URLField(default="http://localhost:3000/question/?p=1")
    previous = serializers.URLField(default="http://localhost:3000/question/?p=1")
    results = QuestionResponse(many=True)

class FieldValuesResponse(serializers.Serializer):
    class Meta:
        ref_name = 'FieldValues'

    pengguna = serializers.ListField(child=serializers.CharField())
    judul = serializers.ListField(child=serializers.CharField())
    topik = serializers.ListField(child=serializers.CharField())
