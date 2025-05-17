from django.urls import path, include

urlpatterns = [
   path('t/', include('api.v1.teams.urls')), 
   path('u/', include('api.v1.users.urls')), 
   path('token/', include('djoser.urls.jwt', namespace="token"))
]
