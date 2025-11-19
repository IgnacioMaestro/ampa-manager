from datetime import date
from typing import List, Optional

from django.conf import settings
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.charge.models.fee.fee import Fee
from ampa_manager.charge.models.membership_receipt import MembershipReceipt
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.remittance_utils import RemittanceUtils
from ampa_manager.charge.use_cases.remittance_creator_error import RemittanceCreatorError
from ampa_manager.family.models.family import Family


class MembershipRemittanceCreator:
    def __init__(self, families: QuerySet[Family], course: AcademicCourse, payment_date: date):
        self.__families = families
        self.__course = course
        self.__payment_date = payment_date
        self.__sepa_id = RemittanceUtils.get_next_sepa_id()
        self.__concept = settings.MEMBERSHIP_REMITTANCE_CONCEPT

    def create(self) -> tuple[Optional[MembershipRemittance], Optional[RemittanceCreatorError]]:
        remittance: MembershipRemittance = MembershipRemittance(
            course=self.__course, name=self.__generate_remittance_name(), sepa_id=self.__sepa_id,
            payment_date=self.__payment_date, concept=self.__concept)
        receipts: List[MembershipReceipt]
        error: Optional[RemittanceCreatorError]
        receipts, error = self.__create_membership_receipts(remittance)
        if error:
            return None, error
        remittance.save()
        MembershipReceipt.objects.bulk_create(receipts)
        return remittance, None

    def __create_membership_receipts(self, remittance: MembershipRemittance) -> tuple[
        Optional[list[MembershipReceipt]], Optional[RemittanceCreatorError]]:
        membership_receipts: List[MembershipReceipt] = []
        family: Family
        for family in self.__families.iterator():
            if not family.membership_holder or not family.membership_holder.bank_account or not family.membership_holder.bank_account.swift_bic:
                return None, RemittanceCreatorError.BIC_ERROR
            if not family.decline_membership:
                membership_receipt: MembershipReceipt = MembershipReceipt(
                    remittance=remittance, family=family, holder=family.membership_holder)
                membership_receipts.append(membership_receipt)
        if not membership_receipts:
            return None, RemittanceCreatorError.NO_FAMILIES
        try:
            Fee.objects.get(academic_course=remittance.course)
        except Fee.DoesNotExist:
            return None, RemittanceCreatorError.NO_FEE_FOR_COURSE
        return membership_receipts, None

    def __generate_remittance_name(self):
        return _('Members fee') + ' ' + str(self.__course)
