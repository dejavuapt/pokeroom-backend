from rest_framework import serializers
from apps.core.teams.models import Team, Membership, TeamInviteLink
from apps.core.teams.choices import MembershipRoleChoice
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class MembershipSerializer(serializers.ModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all(), required=False)
    # team = serializers.PrimaryKeyRelatedField(read_only = True, many = True)
    class Meta: 
        model = Membership
        fields = ('user', 'team', 'role', 'invited_at')
    
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
    owner_id = serializers.PrimaryKeyRelatedField(queryset = UserModel.objects.all(), 
                                                  required = False, 
                                                  default = None, 
                                                  allow_null = True)
    
    class Meta:
        model = Team
        fields = ('id','name', 'description', 'owner_id') 
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        _id = representation.pop('id')
        user = self.context.get('user')
        return {
            "team_id": _id,
            'owner': str(representation.pop('owner_id')),
            "data": representation,
            'role': str(MembershipRoleChoice(user.member_in.filter(team_id = instance).first().role).label)
        }
        
    def create(self, validated_data):
        owner_id = self.context.get('user').username
        if validated_data.get('owner_id') is not None and validated_data.get('owner_id') != str(self.context.get('user').id):
            raise ValueError(f"Can't create team for another user.")
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
    

class InviteLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamInviteLink
        fields = ('token', 'expires_at')
        extra_kwargs = {'token': {'read_only': True}, 
                        'expires_at': {'read_only': True}}
        
    def create(self, validated_data):
        tid = self.context.get('team_id')
        if tid is None:
            raise ValueError("Need team id to create token.")
        if not TeamInviteLink.objects.filter(team_id = tid).exists():
            til = TeamInviteLink.objects.create(team_id = Team.objects.get(id = tid))
            til.save()
        else:
            raise ValueError("Invite link existed.")
        
        return til