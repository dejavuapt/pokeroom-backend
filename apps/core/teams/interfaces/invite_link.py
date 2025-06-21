from datetime import datetime, timedelta
from django.db import models
from django.utils.translation import gettext as _
from django.utils import timezone
from pokeroom_backend import constants

import secrets, uuid

# TODO: Write a logic to check all models with invitelinkinterface to drop a links that expires
class InviteLinkInterface(models.Model):
    """ 
        Abstract model for storing invite links. \n
        Based on 16 bytes and default expires at 1 day (24h) from created (added in db) \n
        That class haven't `is_expires` field. If you need to check it: do attribute in your class or create logic.
    """
    _token_nbytes: int = constants.TOKEN_NBYTES     
    
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    token = models.CharField(
        _("Token"),
        max_length = 100,
        default = "%s" % (secrets.token_urlsafe(_token_nbytes)),
        editable=False, 
        unique=True
    )
    created_at = models.DateTimeField(
        _("Token created date"),
        default = timezone.now,
        editable=False
    )
    expires_at = models.DateTimeField(
        _("Token expires date"),
        default = timezone.now() + timedelta(days=1),
        editable=False
    )
    
    class Meta:
        abstract = True
        
    def __repr__(self):
        return '%s expires at %s' % (self.get_token(), self.get_expires_date())
    