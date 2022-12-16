from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_members_manager.charge.models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ampa_members_manager.charge.state import State


class AfterSchoolReceipt(models.Model):
    amount = models.FloatField(null=True, blank=True, verbose_name=_("Total (€)"))
    state = models.IntegerField(choices=State.choices, default=State.CREATED, verbose_name=_("State"))
    after_school_registration = models.ForeignKey(
        to=AfterSchoolRegistration, on_delete=CASCADE, verbose_name=_("After School registrations"))
    remittance = models.ForeignKey(
        to=AfterSchoolRemittance, on_delete=CASCADE, verbose_name=_("After School remittance"))

    class Meta:
        verbose_name = _('After School Receipt')
        verbose_name_plural = _('After School Receipts')
