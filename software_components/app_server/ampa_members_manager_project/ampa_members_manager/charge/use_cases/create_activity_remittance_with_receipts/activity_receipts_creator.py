from typing import List

from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_members_manager.charge.models.activity_receipt import ActivityReceipt, NotFound
from ampa_members_manager.charge.models.activity_remittance import ActivityRemittance


class ActivityReceiptsCreator:
    def __init__(self, activity_remittance: ActivityRemittance):
        self.__activity_remittance: ActivityRemittance = activity_remittance

    def create(self):
        activity_registrations: List[ActivityRegistration] = []
        for single_activity in self.__activity_remittance.single_activities.all():
            activity_registrations.extend(ActivityRegistration.with_single_activity(single_activity=single_activity))
        for activity_registration in activity_registrations:
            self.__create_receipt_for_activity_registration(activity_registration)

    def __create_receipt_for_activity_registration(self, activity_registration: ActivityRegistration):
        activity_receipt: ActivityReceipt = self.find_or_create_receipt(activity_registration)
        activity_receipt.activity_registrations.add(activity_registration)
        activity_receipt.save()

    def find_or_create_receipt(self, activity_registration: ActivityRegistration) -> ActivityReceipt:
        try:
            return ActivityReceipt.find_activity_receipt_with_bank_account(
                activity_remittance=self.__activity_remittance, bank_account=activity_registration.bank_account)
        except NotFound:
            price: float = activity_registration.single_activity.calculate_price(
                times=activity_registration.amount, membership=activity_registration.is_membership())
            return ActivityReceipt.objects.create(remittance=self.__activity_remittance, amount=price)
