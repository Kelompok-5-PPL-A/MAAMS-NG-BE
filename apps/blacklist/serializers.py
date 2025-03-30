from rest_framework import serializers
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

    @classmethod
    def format_response(cls, npm, blacklist=None):
        # Direct data formatting instead of serializer validation
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

class BlacklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blacklist
        fields = ['id', 'npm', 'startDate', 'endDate', 'keterangan']

    def validate(self, data):
        if data['endDate'] < data['startDate']:
            raise serializers.ValidationError("End date cannot be before start date")
        return data