import re
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext, gettext_lazy as _
from localflavor.generic.models import IBANField

from ampa_manager.dynamic_settings.singleton import Singleton


class DynamicSetting(Singleton):
    remittances_party_id = models.CharField(max_length=500, verbose_name=_("Party identification"))
    remittances_generic_org_id = models.CharField(max_length=500, verbose_name=_("Generic organisation identification"))
    remittances_bic = models.CharField(max_length=500, verbose_name=_("BIC"))
    remittances_iban = IBANField(verbose_name=_("IBAN"))
    remittances_custody_bic = models.CharField(max_length=500, verbose_name=_("Custody BIC"))
    remittances_custody_iban = IBANField(verbose_name=_("Custody IBAN"))

    custody_members_discount_percent = models.FloatField(
        verbose_name=_("Members discount"),
        help_text=_('Percentage discounted to members in the price of the custody'),
        default=27.0)
    custody_max_days_to_charge_percent = models.IntegerField(
        verbose_name=_("Max days to charge"),
        help_text=_('Maximum number of days in a month (as a percentage) to charge to each user'),
        default=80)
    family_email_domain = models.CharField(
        max_length=200, blank=True, default='', verbose_name=_('Family email domain'),
        help_text=_('If set, imported family emails must use this domain. Example: @abendanoikastola.com'))

    class Meta:
        verbose_name = _('Setting')
        verbose_name_plural = _('Settings')

    def __str__(self):
        return gettext('Settings')

    def clean(self):
        super().clean()
        self.family_email_domain = self.normalize_email_domain(self.family_email_domain)
        if self.family_email_domain and not self.is_valid_email_domain(self.family_email_domain):
            raise ValidationError({
                'family_email_domain': _('Enter a domain like @abendanoikastola.com')
            })

    def save(self, *args, **kwargs):
        self.family_email_domain = self.normalize_email_domain(self.family_email_domain)
        super().save(*args, **kwargs)

    @classmethod
    def required_family_email_domain(cls) -> str:
        domain = cls.objects.filter(pk=1).values_list('family_email_domain', flat=True).first()
        return cls.normalize_email_domain(domain)

    @classmethod
    def family_email_matches_required_domain(cls, email: Optional[str]) -> bool:
        domain = cls.required_family_email_domain()
        if not domain or not email:
            return True
        return email.lower().endswith(domain)

    @staticmethod
    def normalize_email_domain(domain: Optional[str]) -> str:
        if not domain:
            return ''
        normalized = str(domain).strip().lower().replace(' ', '')
        if normalized and not normalized.startswith('@'):
            normalized = f'@{normalized}'
        return normalized

    @staticmethod
    def is_valid_email_domain(domain: str) -> bool:
        return bool(re.match(r'^@[a-z0-9.-]+\.[a-z]{2,}$', domain))
