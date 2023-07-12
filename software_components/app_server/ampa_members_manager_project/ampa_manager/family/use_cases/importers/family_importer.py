from typing import Optional

from ampa_manager.family.models.family import Family
from ampa_manager.family.models.membership import Membership
from ampa_manager.utils.excel.import_model_result import ImportModelResult


class FamilyImporter:

    @staticmethod
    def import_family(family_surnames: str, parent1_name_and_surnames: Optional[str] = None,
                      parent2_name_and_surnames: Optional[str] = None, set_as_member=False,
                      child_name: Optional[str] = None) -> ImportModelResult:
        result = ImportModelResult(Family.__name__, [family_surnames])

        if family_surnames:
            parents_name_and_surnames = []
            if parent1_name_and_surnames:
                parents_name_and_surnames.append(parent1_name_and_surnames)
            if parent2_name_and_surnames:
                parents_name_and_surnames.append(parent2_name_and_surnames)

            family, error = Family.find(family_surnames, parents_name_and_surnames, child_name)

            if family:
                result.set_not_modified(family)
            elif error:
                result.set_error(error)
            elif family_surnames:
                family = Family.objects.create(surnames=family_surnames)
                result.set_created(family)

            if set_as_member and family and not Membership.is_member_family(family):
                Membership.make_member_for_active_course(family)

        else:
            result.set_error('Missing surnames')

        return result
