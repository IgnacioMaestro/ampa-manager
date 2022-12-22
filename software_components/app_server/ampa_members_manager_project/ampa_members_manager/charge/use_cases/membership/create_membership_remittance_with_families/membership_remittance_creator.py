from typing import List, Optional

from django.db.models import QuerySet

from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.charge.models.membership_receipt import MembershipReceipt
from ampa_members_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_members_manager.family.models.family import Family


class MembershipRemittanceCreator:
    def __init__(self, families: QuerySet[Family], course: AcademicCourse):
        self.__families = families
        self.__course = course

    def create(self) -> Optional[MembershipRemittance]:
        membership_remittance: MembershipRemittance = MembershipRemittance(course=self.__course)
        membership_receipts: List[MembershipReceipt] = []
        for family in self.__families.iterator():
            if not family.decline_membership:
                membership_receipt: MembershipReceipt = MembershipReceipt(remittance=membership_remittance, family=family)
                membership_receipts.append(membership_receipt)
        if not membership_receipts:
            return None
        membership_remittance.save()
        MembershipReceipt.objects.bulk_create(membership_receipts)
        return membership_remittance
