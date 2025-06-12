from rest_framework import serializers
from apps.core.teams.models import Team, Membership
from apps.core.teams.choices import MembershipRoleChoice
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class MembershipSerializer(serializers.ModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all(), required=False)
    # team = serializers.PrimaryKeyRelatedField(read_only = True, many = True)
    class Meta: 
        model = Membership
        fields = ('user', 'role', 'invited_at')
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        _id = representation.pop('user')
        representation['role'] = str(MembershipRoleChoice(representation.get('role')).label)
        return {
            "username": UserModel.objects.get(pk=_id).get_username(),
            "data": representation
        }


class TeamSreializer(serializers.ModelSerializer):
    # members = MembershipSerializer(read_only=True, many=True)
    
    class Meta:
        model = Team
        fields = ('id','name', 'description', 'created_at', 'owner_id') 
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        _id = representation.pop('id')
        user = self.context.get('user')
        return {
            "team_id": _id,
            'owner_id': str(representation.pop('owner_id')),
            "data": representation,
            'role': str(MembershipRoleChoice(user.member_in.filter(team_id = instance).first().role).label)
        }
        
        
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
        return team
    