import re
from rest_framework import serializers
from .models import Causes

class BaseCauses(serializers.Serializer):
    MODE_CHOICES = Causes.ModeChoices

    class Meta:
        ref_name = 'BaseCauses'
        
    cause = serializers.CharField()

    def validate_cause(self, value):
        dangerous_patterns = [
            # SQL Injection patterns
            r"(\b(SELECT|UNION|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|;|--)\b)",
            r"'.*'",
            r"'.*OR.*'",
            r"'.*UNION.*'",
            r"'.*DROP.*'",

            # XSS patterns
            r"<script.*?>.*?</script.*?>",
            r"onerror\s*=",
            r"javascript:",
            r"<img.*?on.*?=",
            r"<a.*?href.*?javascript:",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise serializers.ValidationError("Input contains potentially dangerous SQL or XSS content.")
                
        return value

class CausesRequest(BaseCauses):
    class Meta:
        ref_name = 'CausesRequest'

    MODE_CHOICES = Causes.ModeChoices

    question_id = serializers.UUIDField()
    cause = serializers.CharField()
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