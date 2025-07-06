from django.urls import path, include
from rest_framework.schemas import get_schema_view

urlpatterns = [
   path('u/', include(('api.v1.users.urls', 'apps.core.users'), namespace="users")), 
   path('games/', include(('api.v1.games.urls', 'apps.games'), namespace="games")),
   path('token/', include(('djoser.urls.jwt', 'djoser'), namespace="token")),
   path(
      'docs/',
      get_schema_view(
         title = "Pokeroom API", version = '1.0.0',
      ),
      name = 'openapi-schema'
   )
]
