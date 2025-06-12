from django.urls import path, include
from rest_framework import routers
from .views import TeamViewSet

app_name = 'apps.core.teams'

router = routers.DefaultRouter()
router.register('', TeamViewSet, basename='teams')

urlpatterns = [
    path('', include(router.urls))
    # path('', APITeam.as_view(), name='teams_list'),
    # path('<team_id>/', api_team_detail, name='api_team_detail' )
] 