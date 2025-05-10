from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
from django.utils import timezone
import uuid

class PokeroomUser(AbstractUser):
    
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    username = models.CharField(
        verbose_name = _("username"),
        max_length=50,
        unique=True,
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
    image_url = models.ImageField(_("image url"),null=True,default=None,blank=True)
    created_at = models.DateTimeField(_("created at"),default=timezone.now)
    telegram_id = models.CharField("telegram id",max_length=20,null=True,default=None,blank=True)
    
    class Meta:
        verbose_name = "puser"
        verbose_name_plural = "pusers"
        
    def __str__(self):
        return "%s (%s)" % (self.get_full_name(), self.get_username())
    
    # GETTERS
    
    def get_image_url(self):
        return getattr(self, "image_url")
    
    def get_when_created(self):
        return getattr(self, "created_at")
    
    def get_telegram_id(self):
        return getattr(self, "telegram_id")
    
    