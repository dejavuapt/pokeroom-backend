from django.contrib.auth import get_user_model
from rest_framework import serializers

UserModel = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    # teams = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = UserModel
        fields = ('id', 'username', 'first_name', 'last_name', 
                  'email', 'image_url', 'telegram_id')
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        _id = representation.pop('id')
        return {
            "id": _id,
            "data": representation
        }
