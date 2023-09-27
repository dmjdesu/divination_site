from rest_framework import serializers
from .models import User ,Messages


class MessageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Messages
        fields = ['sender_name', 'receiver_name', 'description', 'time']