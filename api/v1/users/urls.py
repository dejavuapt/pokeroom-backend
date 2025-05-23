from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet
from djoser import views
app_name = "apps.core.users"

router = routers.DefaultRouter()
router.register('', UserViewSet, basename='u')

urlpatterns = [
    path('', include(router.urls))
]