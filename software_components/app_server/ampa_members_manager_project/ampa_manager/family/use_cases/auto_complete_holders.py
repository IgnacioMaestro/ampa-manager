from typing import Optional

from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder


class AutoCompleteHolders:

    @classmethod
    def complete_holders(cls, family: Family):
        cls.complete_membership_holder(family)
        cls.complete_custody_holder(family)
        cls.complete_after_school_holder(family)
        cls.complete_camps_holder(family)

    @classmethod
    def complete_membership_holder(cls, family: Family):
        if not family.membership_holder:
            last_created_holder = cls.get_last_created_holder(family)
            if last_created_holder:
                family.membership_holder = last_created_holder
                family.save()
                return

    @classmethod
    def complete_camps_holder(cls, family: Family):
        if not family.camps_holder:
            last_registration_holder = cls.get_last_registration_holder(CampsRegistration, family)
            if last_registration_holder:
                family.camps_holder = last_registration_holder
                family.save()
                return
            if family.membership_holder:
                family.camps_holder = family.membership_holder
                family.save()
                return
            last_created_holder = cls.get_last_created_holder(family)
            if last_created_holder:
                family.camps_holder = last_created_holder
                family.save()
                return

    @classmethod
    def complete_after_school_holder(cls, family: Family):
        if not family.after_school_holder:
            last_registration_holder = cls.get_last_registration_holder(AfterSchoolRegistration, family)
            if last_registration_holder:
                family.after_school_holder = last_registration_holder
                family.save()
                return
            if family.membership_holder:
                family.after_school_holder = family.membership_holder
                family.save()
                return
            last_created_holder = cls.get_last_created_holder(family)
            if last_created_holder:
                family.after_school_holder = last_created_holder
                family.save()
                return

    @classmethod
    def complete_custody_holder(cls, family: Family):
        if not family.custody_holder:
            last_registration_holder = cls.get_last_registration_holder(CustodyRegistration, family)
            if last_registration_holder:
                family.custody_holder = last_registration_holder
                family.save()
                return
            if family.membership_holder:
                family.custody_holder = family.membership_holder
                family.save()
                return
            last_created_holder = cls.get_last_created_holder(family)
            if last_created_holder:
                family.custody_holder = last_created_holder
                family.save()
                return

    @classmethod
    def get_last_registration_holder(cls, registration_model, family: Family) -> Optional[Holder]:
        registrations = registration_model.objects.of_family(family).order_by('-id')
        if registrations.exists():
            return registrations.first().holder
        return None

    @classmethod
    def get_last_created_holder(cls, family: Family) -> Optional[Holder]:
        holders = Holder.objects.of_family(family).order_by('-id')
        if holders.exists():
            return holders.first()
        return None
