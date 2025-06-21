from django.contrib.auth import get_user_model
from api.v1.users.serializers import UserSerializer
from djoser import views

import logging
logger = logging.getLogger('api')

UserModel = get_user_model()

class PokeroomUserViewSet(views.UserViewSet):
    serializer_class = UserSerializer
    
    def create(self, request, *args, **kwargs):
        logger.debug(f"{request.data}")
        return super().create(request, *args, **kwargs)