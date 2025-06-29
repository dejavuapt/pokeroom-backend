from django.urls import path, include
from rest_framework import routers
from .views import PokerGameViewset, PokergameDoViewset

app_name = 'apps.games'

router = routers.DefaultRouter()
router.register(r'(?P<id>[0-9a-f-]+)/poker', PokerGameViewset, basename='poker-game')
router.register(r'(?P<id>[0-9a-f-]+)/poker', PokergameDoViewset, basename='poker-game-do')

urlpatterns = [
    path('', include(router.urls))
] 