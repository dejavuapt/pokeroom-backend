from django.urls import path, include
from rest_framework import routers
from .views import PokerGameViewset, StateViewset, PlayersViewset, TaskEvaluationViewset

app_name = 'apps.games'

router = routers.DefaultRouter()
router.register(r'poker', PokerGameViewset, basename='poker-game')
router.register(r'poker/(?P<id>[0-9a-f-]+)/state', StateViewset, basename='poker-state')
router.register(r'poker/(?P<id>[0-9a-f-]+)/players', PlayersViewset, basename='poker-players')
router.register(r'poker/(?P<id>[0-9a-f-]+)/tasks', TaskEvaluationViewset, basename='poker-tasks')
# router.register(r'poker/(?P<id>[0-9a-f-]+)', PokergameDoViewset, basename='poker-game-do')

urlpatterns = [
    path('', include(router.urls))
] 