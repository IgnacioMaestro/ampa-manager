from django.db.models import QuerySet

from ampa_members_manager.activity.models.activity_period import ActivityPeriod
from ampa_members_manager.charge.use_cases.create_activity_remittance_with_receipts.activity_receipts_creator import \
    ActivityReceiptsCreator
from ampa_members_manager.charge.models.activity_remittance import ActivityRemittance


class ActivityRemittanceWithReceiptsCreator:
    def __init__(self, payable_parts: QuerySet[ActivityPeriod]):
        self.__payable_parts: QuerySet[ActivityPeriod] = payable_parts

    def create(self):
        activity_remittance: ActivityRemittance = ActivityRemittance.create_filled(
            payable_parts=self.__payable_parts)
        ActivityReceiptsCreator(activity_remittance).create()
