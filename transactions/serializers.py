from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Transaction, Profile

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['user']

class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role')
    updated_at = serializers.DateTimeField(source='profile.updated_at')
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'role', 'date_joined', 'updated_at']

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username