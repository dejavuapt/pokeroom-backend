from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _

class PokeroomUser(AbstractUser):
    
    username = models.CharField(
        verbose_name = _("username"),
        max_length=50,
        unique=True,
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(_("email address"), blank=True)