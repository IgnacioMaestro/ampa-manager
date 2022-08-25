from django.db import models
from django.utils.translation import gettext_lazy as _


class State(models.IntegerChoices):
    NOT_SENT = (1, _('Not sent'))
    SENT = (2, _('Sent'))
    SIGNED = (3, _('Signed'))
