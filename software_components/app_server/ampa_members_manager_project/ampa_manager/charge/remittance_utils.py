from django.utils import timezone

from .models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from .models.camps.camps_remittance import CampsRemittance
from .models.custody.custody_remittance import CustodyRemittance
from .models.membership_remittance import MembershipRemittance


class RemittanceUtils:

    @classmethod
    def get_next_sepa_id(cls) -> str:
        custody_count = CustodyRemittance.objects.paid_on_current_year().count()
        after_school_count = AfterSchoolRemittance.objects.paid_on_current_year().count()
        membership_count = MembershipRemittance.objects.paid_on_current_year().count()
        camps_count = CampsRemittance.objects.paid_on_current_year().count()
        total_count = custody_count + after_school_count + membership_count + camps_count
        total_with_zeros = str(total_count + 1).zfill(3)
        return f'{timezone.now().year}/{total_with_zeros}'
