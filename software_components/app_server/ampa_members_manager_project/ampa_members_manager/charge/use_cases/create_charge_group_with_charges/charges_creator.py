from typing import List

from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_members_manager.charge.models.charge import Charge, NotFound
from ampa_members_manager.charge.models.charge_group import ChargeGroup


class ChargesCreator:
    @classmethod
    def create(cls, charge_group: ChargeGroup):
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
