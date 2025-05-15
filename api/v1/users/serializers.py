from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser import serializers as djoser_serializers
from djoser.conf import settings
from apps.core.teams.models import Team

UserModel = get_user_model()
       
class UserRepresentMixin:
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        _id = representation.pop('id')
        return {
            "id": _id,
            "data": representation
        }

# Отображает ли он только аутентифицированных пользователь? Он отображает только пользователи если HIDE USERS = True по-умолчанию
class UserSerializer(UserRepresentMixin, djoser_serializers.UserSerializer):
    # teams = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = UserModel
        fields = ('id', 'username', 'first_name', 'last_name', 
                  'email', 'image_url')
    
    

class CurrentUserSerializer(UserRepresentMixin, djoser_serializers.UserSerializer):
    teams = serializers.PrimaryKeyRelatedField(queryset = Team.objects.all(), many = True) 
    
    class Meta:
        model = UserModel
        fields = ('id', 'username', 'first_name', 'last_name',
                  'email', 'image_url', 'telegram_id', 'teams')