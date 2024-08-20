from typing import Optional

from django.db.models import QuerySet

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.use_cases.membership.create_membership_remittance_with_families.membership_remittance_creator import \
    MembershipRemittanceCreator
from ampa_manager.charge.use_cases.remittance_creator_error import RemittanceCreatorError
from ampa_manager.family.models.family import Family


class MembershipRemittanceCreatorOfActiveCourse:
    @classmethod
    def create(cls) -> tuple[Optional[MembershipRemittance], Optional[RemittanceCreatorError]]:
        academic_course: AcademicCourse = ActiveCourse.load()
        families: QuerySet[Family] = Family.objects.members().not_included_in_receipt_of_course(academic_course)
        if not families.exists():
            return None, RemittanceCreatorError.NO_FAMILIES
        return MembershipRemittanceCreator(families, course=academic_course).create()
