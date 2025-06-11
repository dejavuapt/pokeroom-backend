from django.urls import path, include

urlpatterns = [
   path('t/', include('api.v1.teams.urls', namespace="teams")), 
   path('u/', include('api.v1.users.urls', namespace="users")), 
   path('token/', include(('djoser.urls.jwt', 'djoser'), namespace="djoser_token"))
]
