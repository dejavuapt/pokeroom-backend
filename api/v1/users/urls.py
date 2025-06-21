from django.urls import path, include
from rest_framework import routers
from .views import PokeroomUserViewSet
app_name = "apps.core.users"

router = routers.DefaultRouter()
router.register('', PokeroomUserViewSet, basename='u')

urlpatterns = [
    path('', include(router.urls))
]