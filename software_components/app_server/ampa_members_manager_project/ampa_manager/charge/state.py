from django.db import models
from django.utils.translation import gettext_lazy as _


class State(models.IntegerChoices):
    CREATED = (1, _('Created'))
    SEND = (2, _('Sent'))
    PAID = (3, _('Paid'))
