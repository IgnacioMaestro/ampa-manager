from django.db.models import QuerySet

from ampa_members_manager.activity.models.activity_period import ActivityPeriod
from ampa_members_manager.charge.use_cases.activity.create_activity_remittance_with_receipts.activity_receipts_creator import \
    ActivityReceiptsCreator
from ampa_members_manager.charge.models.activity_remittance import ActivityRemittance


class ActivityRemittanceWithReceiptsCreator:
    def __init__(self, activity_periods: QuerySet[ActivityPeriod]):
        self.__activity_periods: QuerySet[ActivityPeriod] = activity_periods

    def create(self):
        activity_remittance: ActivityRemittance = ActivityRemittance.create_filled(
            activity_periods=self.__activity_periods)
        ActivityReceiptsCreator(activity_remittance).create()
        return activity_remittance
