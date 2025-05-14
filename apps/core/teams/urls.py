from django.urls import path

from .views import api_team_detail, APITeam

app_name = 'apps.core.teams'

urlpatterns = [
    path('', APITeam.as_view(), name='teams_list'),
    path('<team_id>/', api_team_detail, name='api_team_detail' )
] 