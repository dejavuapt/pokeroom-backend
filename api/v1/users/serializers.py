from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser import serializers as djoser_serializers
from djoser.conf import settings
import logging

UserModel = get_user_model()


logger = logging.getLogger("api")
       
class UserRepresentMixin:
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        _id = representation.pop('id')
        return {
            "id": _id,
            "data": representation
        }
        
class UserCreateSerializer(UserRepresentMixin, djoser_serializers.UserCreateSerializer):
    telegram_id = serializers.IntegerField(required=False)
    
    class Meta:
        model = UserModel
        fields = ('id', 'username', 'email', 'password', 'telegram_id')
        extra_kwargs = {'password': {'write_only': True}}

# Отображает ли он только аутентифицированных пользователь? Он отображает только пользователи если HIDE USERS = True по-умолчанию
class UserSerializer(UserRepresentMixin, djoser_serializers.UserSerializer):
    # teams = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = UserModel
        fields = ('id', 'username', 'first_name', 'last_name', 
                  'email', 'image_url')
        
class CurrentUserSerializer(UserRepresentMixin, djoser_serializers.UserSerializer):
    
    class Meta:
        model = UserModel
        fields = ('id', 'username', 'first_name', 'last_name',
                  'email', 'image_url', 'telegram_id')