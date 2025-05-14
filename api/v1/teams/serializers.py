from rest_framework import serializers
from apps.core.teams.models import Team, TeamMember
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class MembershipSerializer(serializers.ModelSerializer):
    user_id = serializers.StringRelatedField(read_only=True, many=True)
    
    class Meta: 
        model = TeamMember
        fields = ('user_id', 'role', 'invited_at')

class TeamSreializer(serializers.ModelSerializer):
    members = MembershipSerializer(read_only=True, many=True)
    
    class Meta:
        model = Team
        fields = ('name', 'description', 'owner_id', 'created_at', 'members')
        
    def create(self, validated_data):
        owner_id = validated_data.get('owner_id')
        try:
            owner = UserModel.objects.get(username=owner_id)
        except UserModel.DoesNotExist:
            raise ValueError(f"User with id {owner_id} does not exist.")
        team = Team(
            name = validated_data.get('name'),
            description = validated_data.get('description'),
            owner_id = owner
        )
        team.save()
        team.create_member_by_owner()
        return team