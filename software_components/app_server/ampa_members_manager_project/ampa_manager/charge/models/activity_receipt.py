from __future__ import annotations

from django.db import models
from django.db.models import CASCADE, Manager
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_manager.charge.models.activity_receipt_queryset import ActivityReceiptQuerySet
from ampa_manager.charge.models.activity_remittance import ActivityRemittance
from ampa_manager.charge.models.receipt_exceptions import NoBankAccountException
from ampa_manager.charge.receipt import Receipt, AuthorizationReceipt
from ampa_manager.charge.state import State
from ampa_manager.family.models.holder.holder import Holder


class NotFound(Exception):
    pass


class ActivityReceipt(models.Model):
    amount = models.FloatField(null=True, blank=True, verbose_name=_("Total (€)"))
    state = models.IntegerField(choices=State.choices, default=State.CREATED, verbose_name=_("State"))
    activity_registrations = models.ManyToManyField(to=ActivityRegistration, verbose_name=_("Activity registrations"))
    remittance = models.ForeignKey(to=ActivityRemittance, on_delete=CASCADE, verbose_name=_("Activity remittance"))

    objects = Manager.from_queryset(ActivityReceiptQuerySet)()

    class Meta:
        verbose_name = _('Activity Receipt')
        verbose_name_plural = _('Activity Receipts')
        db_table = 'activity_receipt'

    def check_holder(self, holder: Holder) -> bool:
        for activity_registration in self.activity_registrations.all():
            if activity_registration.holder == holder:
                return True
        return False

    def generate_receipt(self) -> Receipt:
        activity_registration: ActivityRegistration = self.activity_registrations.first()
        if not activity_registration:
            raise NoBankAccountException

        holder: Holder = activity_registration.holder

        authorization: AuthorizationReceipt = AuthorizationReceipt(
            number=holder.authorization_full_number, date=holder.authorization_sign_date)
        return Receipt(
            amount=self.amount, bank_account_owner=str(holder.parent), iban=holder.bank_account.iban,
            bic=holder.bank_account.swift_bic, authorization=authorization)

    @classmethod
    def find_activity_receipt_with_holder(
            cls, activity_remittance: ActivityRemittance, holder: Holder) -> ActivityReceipt:
        for activity_receipt in ActivityReceipt.objects.filter(remittance=activity_remittance):
            if activity_receipt.check_holder(holder=holder):
                return activity_receipt
        raise NotFound
