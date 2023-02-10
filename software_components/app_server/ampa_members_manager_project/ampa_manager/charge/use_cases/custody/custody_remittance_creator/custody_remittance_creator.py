from django.db.models import QuerySet

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.activity.models.custody.custody_registration_queryset import CustodyRegistrationQuerySet
from ....models.custody.custody_receipt import CustodyReceipt
from ....models.custody.custody_remittance import CustodyRemittance


class CustodyRemittanceCreator:
    def __init__(self, editions: QuerySet[CustodyEdition]):
        self.__editions: QuerySet[CustodyEdition] = editions

    def create(self):
        custody_remittance: CustodyRemittance = CustodyRemittance.objects.create_filled(self.__editions)
        custody_registrations: CustodyRegistrationQuerySet = CustodyRegistration.objects.of_custody_remittance(
            custody_remittance)
        custody_registration: CustodyRegistration
        for custody_registration in custody_registrations.iterator():
            CustodyReceipt.objects.create(
                amount=custody_registration.calculate_price(), remittance=custody_remittance,
                custody_registration=custody_registration)
        return custody_remittance
