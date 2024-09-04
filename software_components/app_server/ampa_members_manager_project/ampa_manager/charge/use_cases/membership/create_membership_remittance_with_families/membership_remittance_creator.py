from typing import List, Optional

from django.db.models import QuerySet

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.charge.models.membership_receipt import MembershipReceipt
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.use_cases.remittance_creator_error import RemittanceCreatorError
from ampa_manager.family.models.family import Family


class MembershipRemittanceCreator:
    def __init__(self, families: QuerySet[Family], course: AcademicCourse):
        self.__families = families
        self.__course = course

    def create(self) -> tuple[Optional[MembershipRemittance], Optional[RemittanceCreatorError]]:
        membership_remittance: MembershipRemittance = MembershipRemittance(course=self.__course)
        membership_receipts: List[MembershipReceipt] = []
        family: Family
        for family in self.__families.iterator():
            if not family.membership_holder or not family.membership_holder.bank_account or not family.membership_holder.bank_account.swift_bic:
                return None, RemittanceCreatorError.BIC_ERROR
            if not family.decline_membership:
                membership_receipt: MembershipReceipt = MembershipReceipt(
                    remittance=membership_remittance, family=family, holder=family.membership_holder)
                membership_receipts.append(membership_receipt)
        if not membership_receipts:
            return None, RemittanceCreatorError.NO_FAMILIES
        membership_remittance.save()
        MembershipReceipt.objects.bulk_create(membership_receipts)
        return membership_remittance, None
