from django.db import models
from django.utils.translation import gettext_lazy as _
from localflavor.generic.models import IBANField

from ampa_manager.dynamic_settings.singleton import Singleton


class DynamicSetting(Singleton):
    remittances_party_id = models.CharField(max_length=500, verbose_name=_("Party identification"))
    remittances_generic_org_id = models.CharField(max_length=500, verbose_name=_("Generic organisation identification"))
    remittances_bic = models.CharField(max_length=500, verbose_name=_("BIC"))
    remittances_iban = IBANField(unique=True, verbose_name=_("IBAN"))

    custody_members_discount_percent = models.FloatField(verbose_name=_("Members discount"),
                                                         help_text=_('Percentage discounted to members in the price of '
                                                                     'the custody'))
    custody_max_days_to_charge_percent = models.IntegerField(verbose_name=_("Max days to charge"),
                                                             help_text=_('Maximum number of days in a month (as a '
                                                                         'percentage) to charge to each user'))
