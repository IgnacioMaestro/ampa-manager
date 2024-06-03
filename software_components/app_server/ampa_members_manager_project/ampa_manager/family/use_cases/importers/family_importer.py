from typing import Optional, List

from django.utils.translation import gettext_lazy as _

from ampa_manager.family.models.family import Family
from ampa_manager.family.models.membership import Membership
from ampa_manager.family.use_cases.importers.fields_changes import FieldsChanges
from ampa_manager.utils.excel.import_model_result import ImportModelResult


class FamilyImporter:

    @staticmethod
    def import_family(family_surnames: Optional[str] = None, parent1_name_and_surnames: Optional[str] = None,
                      parent2_name_and_surnames: Optional[str] = None, set_as_member=False,
                      child_name: Optional[str] = None, email: Optional[str] = None) -> ImportModelResult:
        result = ImportModelResult(Family.__name__, [family_surnames])

        if family_surnames or email:
            parents_name_and_surnames = FamilyImporter.append_parents_names_if_not_null(parent1_name_and_surnames,
                                                                                        parent2_name_and_surnames)

            family, error = Family.find(family_surnames, parents_name_and_surnames, child_name, email=email)

            if family:
                if email and not family.email_matches(email):
                    fields_changes = FieldsChanges([family.email], [email], [])
                    family.update_email(email)
                    result.set_updated(family, fields_changes)
                else:
                    result.set_not_modified(family)
            elif error:
                result.set_error(error)
            elif family_surnames:
                family = Family.objects.create(surnames=family_surnames, email=email)
                result.set_created(family)

            if set_as_member and family and not Membership.is_member_family(family):
                Membership.make_member_for_active_course(family)

            if not family:
                result.set_error(_('Unable to find the family'))

        else:
            result.set_error('Missing surnames and email')

        return result

    @staticmethod
    def append_parents_names_if_not_null(parent1_name_and_surnames, parent2_name_and_surnames) -> List[str]:
        parents_name_and_surnames = []
        if parent1_name_and_surnames:
            parents_name_and_surnames.append(parent1_name_and_surnames)
        if parent2_name_and_surnames:
            parents_name_and_surnames.append(parent2_name_and_surnames)
        return parents_name_and_surnames
