from typing import Optional

from ampa_manager.family.models.family import Family
from ampa_manager.management.commands.results.model_import_result import ModelImportResult


class FamilyImporter:

    @staticmethod
    def import_family(family_surnames: str, parent1_name_and_surnames: Optional[str] = None,
                      parent2_name_and_surnames: Optional[str] = None) -> ModelImportResult:
        result = ModelImportResult(Family.__name__, [family_surnames])

        if family_surnames:
            parents_name_and_surnames = []
            if parent1_name_and_surnames:
                parents_name_and_surnames.append(parent1_name_and_surnames)
            if parent2_name_and_surnames:
                parents_name_and_surnames.append(parent2_name_and_surnames)

            family, error = Family.find(family_surnames, parents_name_and_surnames)

            if family:
                result.set_not_modified(family)
            elif error:
                result.set_error(error)
            elif family_surnames:
                family = Family.objects.create(surnames=family_surnames)
                result.set_created(family)
        else:
            result.set_error('Missing surnames')

        return result