from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.family.models.family import Family


class FamilyImporter:

    def __init__(self, family_email: str, family_surnames: str):
        self.result = ImportModelResult(Family)
        self.family_email = family_email
        self.family_surnames = family_surnames
        self.family = None

    def import_family(self) -> ImportModelResult:
        if self.family_email:
            self.family = Family.objects.with_this_email(self.family_email).first()
            if self.family:
                self.manage_found_family()
            else:
                self.manage_not_found_family()
        else:
            self.result.set_error(_('Unable to find, missing email'))

        return self.result

    def manage_not_found_family(self):
        if self.family_surnames:
            family = Family.objects.with_these_surnames(self.family_surnames).first()
            if family:
                self.result.set_error(_('Unable to create, the surnames already exist'))
            else:
                family = Family.objects.create(surnames=self.family_surnames, email=self.family_email)
                self.result.set_created(family)
        else:
            self.result.set_error(_('Email not found, missing surnames'))

    def manage_found_family(self):
        if self.family_surnames and self.family_surnames != self.family.surnames:
            values_before = [self.family.surnames]
            self.family.surnames = self.family_surnames
            values_after = [self.family.surnames]
            self.result.set_updated(self.family, values_before, values_after)
        else:
            self.result.set_not_modified(self.family)
