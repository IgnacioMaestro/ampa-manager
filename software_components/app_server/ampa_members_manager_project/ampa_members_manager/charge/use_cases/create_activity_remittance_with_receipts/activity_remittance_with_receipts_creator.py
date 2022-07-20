from django.db.models import QuerySet

from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.charge.use_cases.create_activity_remittance_with_receipts.charges_creator import ChargesCreator
from ampa_members_manager.charge.models.activity_remittance import ActivityRemittance


class ActivityRemittanceWithReceiptsCreator:
    def __init__(self, single_activities: QuerySet[SingleActivity]):
        self.__single_activities: QuerySet[SingleActivity] = single_activities

    def create(self):
        activity_remittance: ActivityRemittance = ActivityRemittance.create_filled(
            single_activities=self.__single_activities)
        ChargesCreator(activity_remittance).create()