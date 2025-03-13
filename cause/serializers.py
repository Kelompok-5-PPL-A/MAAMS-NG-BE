from rest_framework import serializers
from .models import Causes

class BaseCauses(serializers.Serializer):
    MODE_CHOICES = Causes.ModeChoices

    class Meta:
        ref_name = 'BaseCauses'
        
    cause = serializers.CharField()
    

class CausesRequest(BaseCauses):
    class Meta:
        ref_name = 'CausesRequest'

    MODE_CHOICES = Causes.ModeChoices

    question_id = serializers.UUIDField()
    row = serializers.IntegerField()
    column = serializers.IntegerField()
    mode = serializers.ChoiceField(choices=MODE_CHOICES)


class CausesResponse(BaseCauses):
    class Meta:
        ref_name = 'CausesResponse'
    
    id = serializers.UUIDField()
    question_id = serializers.UUIDField()
    row = serializers.IntegerField()
    column = serializers.IntegerField()
    status = serializers.BooleanField()
    root_status = serializers.BooleanField()
    feedback = serializers.CharField()
