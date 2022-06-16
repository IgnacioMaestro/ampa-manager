from __future__ import annotations

from typing import List

from django.db import models
from django.db.models import CASCADE, QuerySet

from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_members_manager.charge.models.charge_group import ChargeGroup
from ampa_members_manager.charge.models.state import State
from ampa_members_manager.charge.receipt import Receipt
from ampa_members_manager.family.models.authorization import Authorization
from ampa_members_manager.family.models.bank_account import BankAccount


class NotFound(Exception):
    pass


class Charge(models.Model):
    amount = models.FloatField(null=True, blank=True)
    state = models.IntegerField(choices=State.choices, default=State.CREATED)
    activity_registrations = models.ManyToManyField(to=ActivityRegistration)
    group = models.ForeignKey(to=ChargeGroup, on_delete=CASCADE)

    def check_bank_account(self, bank_account: BankAccount) -> bool:
        for activity_registration in self.activity_registrations.all():
            if activity_registration.bank_account == bank_account:
                return True
        return False

    def generate_receipt(self) -> Receipt:
        activity_registration: ActivityRegistration = self.activity_registrations.first()
        bank_account: BankAccount = activity_registration.bank_account
        try:
            authorization: Authorization = Authorization.objects.get(bank_account=bank_account)
            return Receipt(
                amount=self.amount, bank_account_owner=str(bank_account.owner),
                iban=bank_account.iban, authorization=str(authorization))
        except Authorization.DoesNotExist:
            return Receipt(
                amount=self.amount, bank_account_owner=str(bank_account.owner),
                iban=bank_account.iban, authorization='No authorization')

    @classmethod
    def create_charges(cls, charge_group: ChargeGroup):
        activity_registrations: List[ActivityRegistration] = []
        for single_activity in charge_group.single_activities.all():
            activity_registrations.extend(ActivityRegistration.with_single_activity(single_activity=single_activity))
        for activity_registration in activity_registrations:
            charge: Charge
            try:
                charge: Charge = Charge.find_charge_with_bank_account(bank_account=activity_registration.bank_account)
            except NotFound:
                price: float = activity_registration.single_activity.calculate_price(
                    times=activity_registration.amount, membership=activity_registration.is_membership())
                charge: Charge = Charge.objects.create(group=charge_group, amount=price)
            charge.activity_registrations.add(activity_registration)
            charge.save()

    @classmethod
    def find_charge_with_bank_account(cls, bank_account: BankAccount) -> Charge:
        for charge in Charge.objects.all():
            if charge.check_bank_account(bank_account=bank_account):
                return charge
        raise NotFound

    @classmethod
    def create_filled_charges(cls, single_activities: QuerySet[SingleActivity]):
        charge_group: ChargeGroup = ChargeGroup.create_filled_charge_group(single_activities=single_activities)
        Charge.create_charges(charge_group)
