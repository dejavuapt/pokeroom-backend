from django.contrib.auth import get_user_model
from rest_framework import serializers

UserModel = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'image_url', 'created_at', 'telegram_id')
        