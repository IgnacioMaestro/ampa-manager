from typing import Optional

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.use_cases.membership.create_membership_remittance_with_families.membership_remittance_creator import \
    MembershipRemittanceCreator
from ampa_manager.charge.use_cases.remittance_creator_error import RemittanceCreatorError
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.family_queryset import FamilyQuerySet


class MembershipRemittanceCreatorOfActiveCourse:
    @classmethod
    def create(cls) -> tuple[Optional[MembershipRemittance], Optional[RemittanceCreatorError]]:
        academic_course: AcademicCourse = ActiveCourse.load()
        not_included_families: FamilyQuerySet = Family.objects.exclude(
            membershipreceipt__remittance__course=academic_course)
        families: FamilyQuerySet = not_included_families.members_in_course(academic_course)
        if not families.exists():
            return None, RemittanceCreatorError.NO_FAMILIES
        return MembershipRemittanceCreator(families, course=academic_course).create()
