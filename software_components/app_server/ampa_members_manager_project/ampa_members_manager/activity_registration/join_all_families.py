from django.db.models import QuerySet

from ampa_members_manager.activity.models.single_activity import SingleActivity
from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_members_manager.family.models.family import Family


class JoinAllFamilies:

    @classmethod
    def join(cls, single_activity: SingleActivity):
        families: QuerySet[Family] = Family.all_families_with_bank_account()
        for family in families:
            cls.join_family(family, single_activity)

    @classmethod
    def join_family(cls, family: Family, single_activity: SingleActivity):
        ActivityRegistration.objects.create(
            registered_family=family, bank_account=family.default_bank_account, single_activity=single_activity)
