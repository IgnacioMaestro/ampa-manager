from typing import Optional

from django.db.models import QuerySet

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_members_manager.charge.use_cases.create_membership_remittance_with_families.membership_remittance_creator import \
    MembershipRemittanceCreator
from ampa_members_manager.family.models.family import Family


class MembershipRemittanceCreatorOfActiveCourse:
    @classmethod
    def create(cls) -> Optional[MembershipRemittance]:
        families: QuerySet[Family] = Family.objects.members().not_included_in_receipt_of_course(
            ActiveCourse.load())
        if not families.exists():
            return None
        return MembershipRemittanceCreator(families, course=ActiveCourse.load()).create()
