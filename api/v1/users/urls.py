from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet, UserTeamViewSet, UserTeamMembersViewSet
app_name = "apps.core.users"

router = routers.DefaultRouter()
router.register(r'teams/(?P<id>[0-9a-f-]+)/members', UserTeamMembersViewSet, basename='team-members')
router.register('teams', UserTeamViewSet, basename='user-teams')
router.register('', UserViewSet, basename='u')

urlpatterns = [
    path('', include(router.urls))
]