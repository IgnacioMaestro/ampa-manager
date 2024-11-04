from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.membership import Membership


class MembershipImporter:

    def __init__(self, family: Family):
        self.result: ImportModelResult = ImportModelResult(Membership)
        self.family = family
        self.membership = None

    def import_membership(self) -> ImportModelResult:
        if Membership.objects.of_family(self.family).exists():
            self.membership = Membership.objects.of_family(self.family).first()
            self.result.set_not_modified(self.membership)
        else:
            self.membership = Membership.make_member_for_active_course(self.family)
            self.result.set_created(self.membership)

        return self.result
