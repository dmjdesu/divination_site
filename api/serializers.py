from review.models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('username',)
