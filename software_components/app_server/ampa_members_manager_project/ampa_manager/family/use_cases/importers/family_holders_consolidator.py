from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration


class FamilyHoldersConsolidator:
    def __init__(self, family):
        self.family = family

    def consolidate(self):
        if not self.family.custody_holder:
            self.family.custody_holder = self.get_last_custody_registration_holder()
        if not self.family.after_school_holder:
            self.family.after_school_holder = self.get_last_after_school_registration_holder()
        if not self.family.camps_holder:
            self.family.camps_holder = self.get_last_camps_registration_holder()

        if not self.family.membership_holder:
            self.family.membership_holder = self.family.get_default_holder()

        if not self.family.custody_holder:
            self.family.custody_holder = self.family.membership_holder
        if not self.family.after_school_holder:
            self.family.after_school_holder = self.family.membership_holder
        if not self.family.camps_holder:
            self.family.camps_holder = self.family.membership_holder

    def get_last_custody_registration_holder(self):
        registrations = CustodyRegistration.objects.of_family(self.family).order_by('-id')
        if registrations.exists():
            return registrations.last().holder
        return None

    def get_last_after_school_registration_holder(self):
        registrations = AfterSchoolRegistration.objects.of_family(self.family).order_by('-id')
        if registrations.exists():
            return registrations.last().holder
        return None

    def get_last_camps_registration_holder(self):
        registrations = CampsRegistration.objects.of_family(self.family).order_by('-id')
        if registrations.exists():
            return registrations.last().holder
        return None
