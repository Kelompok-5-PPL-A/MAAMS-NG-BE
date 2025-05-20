from rest_framework import serializers
from django.utils import timezone
from apps.blacklist.models import Blacklist

class BlacklistInfoSerializer(serializers.Serializer):
    start_date = serializers.DateField(source='startDate')
    end_date = serializers.DateField(source='endDate')
    reason = serializers.CharField(source='keterangan')
    days_remaining = serializers.IntegerField()

class BlacklistResponseSerializer(serializers.Serializer):
    npm = serializers.CharField()
    is_blacklisted = serializers.BooleanField()
    blacklist_info = BlacklistInfoSerializer(allow_null=True)
    message = serializers.CharField(required=False, allow_null=True)
    
    @classmethod
    def format_response(cls, npm, blacklist=None):
        """
        Format response for blacklist status check.
        
        Args:
            npm: Student's NPM number
            blacklist: Blacklist object if found, None otherwise
            
        Returns:
            Dictionary with formatted response data
        """
        # Direct data formatting without serializer validation
        response_data = {
            "npm": npm,
            "is_blacklisted": blacklist is not None,
            "blacklist_info": None
        }
            
        # If blacklisted, add the details
        if blacklist:
            response_data["blacklist_info"] = {
                "start_date": blacklist.startDate.isoformat(),
                "end_date": blacklist.endDate.isoformat(),
                "reason": blacklist.keterangan,
                "days_remaining": blacklist.days_remaining
            }
                
        return response_data

class BlacklistCreateSerializer(serializers.Serializer):
    npm = serializers.CharField(required=True, max_length=15)
    reason = serializers.CharField(required=True)
    end_date = serializers.DateField(required=True)
    
    def validate(self, data):
        if data['end_date'] <= timezone.now().date():
            raise serializers.ValidationError("End date must be in the future")
        return data

class BlacklistRemoveSerializer(serializers.Serializer):
    npm = serializers.CharField(required=True, max_length=15)

class BlacklistHistorySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    npm = serializers.CharField()
    reason = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    is_active = serializers.BooleanField(required=False)
    days_remaining = serializers.IntegerField()

# class BlacklistSerializer(serializers.ModelSerializer):
#     is_active = serializers.BooleanField(read_only=True)
#     days_remaining = serializers.IntegerField(read_only=True)
    
#     class Meta:
#         model = Blacklist
#         fields = ['id', 'npm', 'startDate', 'endDate', 'keterangan', 'is_active', 'days_remaining']
    
#     def validate(self, data):
#         if data.get('endDate') and data.get('startDate') and data['endDate'] < data['startDate']:
#             raise serializers.ValidationError("End date cannot be before start date")
#         return data