from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Transaction, Profile

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['user']

class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES, source='profile.role')
    updated_at = serializers.DateTimeField(source='profile.updated_at', read_only=True)
    name = serializers.SerializerMethodField()
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'email', 'role', 'date_joined', 'updated_at']
        read_only_fields = ['id', 'date_joined', 'updated_at']

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        role = profile_data.get('role')
        if role:
            instance.profile.role = role
            instance.profile.save()
        return super().update(instance, validated_data)