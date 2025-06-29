from django.urls import re_path
from api.v1.teams.consumers import TeamConsumer

websocket_urlpatterns = [
    re_path(r'ws/t/(?P<id>[0-9a-f-]+)/', TeamConsumer.as_asgi()),
]