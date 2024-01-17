from rest_framework import serializers
from .models import Expense, User
import uuid

class UserSerializer(serializers.ModelSerializer):
    userid = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('userid', 'name', 'email', 'mobileNumber', 'balance', 'owe','to','timestamp')

    def get_userid(self, obj):
        if isinstance(obj.userid, uuid.UUID):
            return obj.userid.hex
        return obj.userid

    def create(self, validated_data):
        # Set default value for 'owe' if not provided in the request
        validated_data.setdefault('owe', 0.0)
        
        # Set default value to None
        validated_data.setdefault('to', None)

        return super(UserSerializer, self).create(validated_data)

class ExpenseSerializer(serializers.ModelSerializer):
    participants_ids = serializers.JSONField(default=list, read_only=True)

    class Meta:
        model = Expense
        fields = ('id', 'payer_id', 'amount', 'type', 'share', 'participants_ids','timestamp')


