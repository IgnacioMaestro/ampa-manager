from django.db import models
from django.utils.translation import gettext_lazy as _
from localflavor.generic.models import IBANField

from ampa_manager.dynamic_settings.singleton import Singleton


class DynamicSetting(Singleton):
    ampa_iban = IBANField(unique=True, verbose_name=_("IBAN"))
    custody_members_discount_percent = models.FloatField(verbose_name=_("Members discount percent"))
    custody_max_days_to_charge_per_month_percent = models.IntegerField(verbose_name=_("Max days percent to charge each month"))
