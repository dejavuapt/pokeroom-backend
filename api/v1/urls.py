from django.urls import path, include

urlpatterns = [
   path('teams/', include('api.v1.teams.urls')), 
   path('users/', include('api.v1.users.urls')), 
]
