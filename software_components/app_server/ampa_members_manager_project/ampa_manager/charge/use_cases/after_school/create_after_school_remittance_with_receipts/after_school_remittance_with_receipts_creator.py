from django.db.models import QuerySet

from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.after_school.after_school_registration_queryset import \
    AfterSchoolRegistrationQuerySet
from ampa_manager.charge.models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from ampa_manager.charge.models.after_school_charge.after_school_remittance import AfterSchoolRemittance


class AfterSchoolRemittanceWithReceiptsCreator:
    def __init__(self, after_school_editions: QuerySet[AfterSchoolEdition]):
        self.__after_school_editions: QuerySet[AfterSchoolEdition] = after_school_editions

    def create(self) -> AfterSchoolRemittance:
        return self.create_with_fraction(1.0)

    def create_with_fraction(self, fraction: float) -> AfterSchoolRemittance:
        after_school_remittance: AfterSchoolRemittance = AfterSchoolRemittance.create_filled(
            self.__after_school_editions)
        after_school_registrations: AfterSchoolRegistrationQuerySet = AfterSchoolRegistration.objects.of_after_school_remittance(
            after_school_remittance)
        for after_school_registration in after_school_registrations.iterator():
            AfterSchoolReceipt.objects.create(
                amount=after_school_registration.calculate_price() * fraction,
                remittance=after_school_remittance, after_school_registration=after_school_registration)
        return after_school_remittance
