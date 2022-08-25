from django.db import models
from django.utils.translation import gettext_lazy as _


class Funding(models.IntegerChoices):
    NO_FUNDING = (1, _('No funding'))
    CULTURAL = (2, _('Cultural'))
    SPORT = (3, _('Sport'))
