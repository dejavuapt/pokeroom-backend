from django.db import models
from django.utils.translation import gettext_lazy as _

class MembershipRoleChoice(models.TextChoices):
    OWNER = 'O', _("Owner")
    MODERATOR = 'M', _("Moderator")
    DEFAULT = 'D', _("Default")