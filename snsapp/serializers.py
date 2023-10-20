from rest_framework import serializers
from .models import Messages
from rest_framework import serializers
from django.contrib.auth import get_user_model

class MessageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Messages
        fields = ['sender_name', 'receiver_name', 'description', 'time']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'points']