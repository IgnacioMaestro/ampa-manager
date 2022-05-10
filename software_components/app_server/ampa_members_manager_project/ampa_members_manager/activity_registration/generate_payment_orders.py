from django.db.models import QuerySet

from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration


class GeneratePaymentOrders:
    @classmethod
    def generate(cls, single_activity: SingleActivity):
        activity_registrations: QuerySet[ActivityRegistration] = ActivityRegistration.with_single_activity(
            single_activity)
        for activity_registration in activity_registrations:
            price: float = single_activity.calculate_price(
                times=activity_registration.amount, membership=activity_registration.is_membership())
            activity_registration.set_payment_order(amount=price)
