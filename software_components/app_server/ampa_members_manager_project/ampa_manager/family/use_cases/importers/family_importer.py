from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.family.models.family import Family


class FamilyImporter:

    @staticmethod
    def import_family(family_email: str, family_surnames: str) -> ImportModelResult:
        result = ImportModelResult(Family.__name__)

        if family_email:
            family: Family = Family.objects.with_this_email(family_email).first()
            if family:
                if family_surnames and family_surnames != family.surnames:
                    values_before = [family.surnames]
                    family.surnames = family_surnames
                    values_after = [family.surnames]
                    result.set_updated(family, values_before, values_after)
                else:
                    result.set_not_modified(family)
            elif family_surnames:
                family = Family.objects.with_these_surnames(family_surnames).first()
                if family:
                    result.set_error(_('Unable to create, the surnames already exist'))
                else:
                    family = Family.objects.create(surnames=family_surnames, email=family_email)
                    result.set_created(family)
        else:
            result.set_error(_('Unable to find, missing email'))

        return result
