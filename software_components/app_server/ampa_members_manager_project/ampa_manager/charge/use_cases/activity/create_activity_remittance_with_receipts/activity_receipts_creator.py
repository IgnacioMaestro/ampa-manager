from typing import List

from ampa_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_manager.charge.models.activity_receipt import ActivityReceipt, NotFound
from ampa_manager.charge.models.activity_remittance import ActivityRemittance


class ActivityReceiptsCreator:
    def __init__(self, activity_remittance: ActivityRemittance):
        self.__activity_remittance: ActivityRemittance = activity_remittance

    def create(self):
        activity_registrations: List[ActivityRegistration] = []
        for activity_period in self.__activity_remittance.activity_periods.all():
            activity_registrations.extend(ActivityRegistration.with_activity_period(activity_period=activity_period))
        for activity_registration in activity_registrations:
            self.create_receipt_for_activity_registration(activity_registration)

    def create_receipt_for_activity_registration(self, activity_registration: ActivityRegistration):
        activity_receipt: ActivityReceipt = self.find_or_create_receipt(activity_registration)
        price: float = activity_registration.activity_period.calculate_price(
            times=activity_registration.amount, membership=activity_registration.is_membership())
        activity_receipt.amount = activity_receipt.amount + price
        activity_receipt.activity_registrations.add(activity_registration)
        activity_receipt.save()

    def find_or_create_receipt(self, activity_registration: ActivityRegistration) -> ActivityReceipt:
        try:
            return ActivityReceipt.find_activity_receipt_with_holder(
                activity_remittance=self.__activity_remittance, holder=activity_registration.holder)
        except NotFound:
            return ActivityReceipt.objects.create(remittance=self.__activity_remittance, amount=0.0)
