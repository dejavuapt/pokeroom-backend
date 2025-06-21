from django.urls import path, include
from rest_framework import routers
from .views.members import MembersViewset
from .views.team import TeamViewset

app_name = 'apps.core.teams'

router = routers.DefaultRouter()
router.register('', TeamViewset, basename='user-teams')
router.register(r'(?P<id>[0-9a-f-]+)/members', MembersViewset, basename='team-members')

urlpatterns = [
    path('', include(router.urls))
    # path('', APITeam.as_view(), name='teams_list'),
    # path('<team_id>/', api_team_detail, name='api_team_detail' )
] 