from django.db.models import QuerySet

from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.models.camps.camps_registration_queryset import CampsRegistrationQuerySet
from ampa_manager.charge.models.camps.camps_receipt import CampsReceipt
from ampa_manager.charge.models.camps.camps_remittance import CampsRemittance


class CampsRemittanceCreator:
    def __init__(self, editions: QuerySet[CampsEdition]):
        self.__editions: QuerySet[CampsEdition] = editions

    def create(self):
        camps_remittance: CampsRemittance = CampsRemittance.objects.create_filled(self.__editions)
        camps_registrations: CampsRegistrationQuerySet = CampsRegistration.objects.of_camps_remittance(
            camps_remittance)
        camps_registration: CampsRegistration
        for camps_registration in camps_registrations.iterator():
            CampsReceipt.objects.create(
                amount=camps_registration.calculate_price(), remittance=camps_remittance,
                camps_registration=camps_registration)
        return camps_remittance
