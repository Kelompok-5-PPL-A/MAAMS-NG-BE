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
    tags = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    def get_tags(self, obj):
        if hasattr(obj.tags, 'all'):
            return [tag.name for tag in obj.tags.all()]
        return obj.tags
    
    def get_user(self, obj):
        return obj.user.uuid if obj.user else None
        
    def get_username(self, obj):
        return obj.user.username if obj.user else None
    
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
