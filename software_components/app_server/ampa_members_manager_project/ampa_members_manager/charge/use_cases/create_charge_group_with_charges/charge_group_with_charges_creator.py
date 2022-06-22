from django.db.models import QuerySet

from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.charge.use_cases.create_charge_group_with_charges.charges_creator import ChargesCreator
from ampa_members_manager.charge.models.charge_group import ChargeGroup


class ChargeGroupWithChargesCreator:
    def __init__(self, single_activities: QuerySet[SingleActivity]):
        self.__single_activities: QuerySet[SingleActivity] = single_activities

    def create(self):
        charge_group: ChargeGroup = ChargeGroup.create_filled_charge_group(single_activities=self.__single_activities)
        ChargesCreator(charge_group).create()
