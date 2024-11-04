from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.family.models.holder.holder import Holder


class FamilyHoldersConsolidator:
    def __init__(self, family):
        self.family = family

    def consolidate(self) -> list[str]:
        warnings = []

        if not self.family.custody_holder:
            self.family.custody_holder = self.get_last_custody_registration_holder()
            warnings.append(_('Family custody holder updated with last registration holder'))
        if not self.family.after_school_holder:
            self.family.after_school_holder = self.get_last_after_school_registration_holder()
            warnings.append(_('Family after-school holder updated with last registration holder'))
        if not self.family.camps_holder:
            self.family.camps_holder = self.get_last_camps_registration_holder()
            warnings.append(_('Family camps holder updated with last registration holder'))

        if not self.family.membership_holder:
            if self.family.custody_holder:
                self.family.membership_holder = self.family.custody_holder
                warnings.append(_('Family membership holder updated with custody holder'))
            elif self.family.camps_holder:
                self.family.membership_holder = self.family.camps_holder
                warnings.append(_('Family membership holder updated with camps holder'))
            elif self.family.after_school_holder:
                self.family.membership_holder = self.family.after_school_holder
                warnings.append(_('Family membership holder updated with after-school holder'))
            else:
                family_holders = Holder.objects.of_family(self).order_by('-id')
                if family_holders.exists():
                    self.family.membership_holder = family_holders.first()
                    warnings.append(_('Family membership holder updated with a last registered holder of the family'))

        if not self.family.custody_holder:
            self.family.custody_holder = self.family.membership_holder
            warnings.append(_('Custody holder updated with membership holder'))
        if not self.family.after_school_holder:
            self.family.after_school_holder = self.family.membership_holder
            warnings.append(_('After-school holder updated with membership holder'))
        if not self.family.camps_holder:
            self.family.camps_holder = self.family.membership_holder
            warnings.append(_('Camps holder updated with membership holder'))

        if len(warnings) > 0:
            self.family.save()

        return warnings

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
