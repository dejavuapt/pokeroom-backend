from rest_framework import serializers
from apps.core.teams.models import Team

class TeamSreializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name', 'description', 'owner_id', 'created_at')