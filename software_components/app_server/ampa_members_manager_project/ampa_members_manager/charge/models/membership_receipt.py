from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_members_manager.charge.state import State
from ampa_members_manager.family.models.family import Family


class MembershipReceipt(models.Model):
    state = models.IntegerField(choices=State.choices, default=State.CREATED, verbose_name=_("State"))
    remittance = models.ForeignKey(to=MembershipRemittance, on_delete=CASCADE, verbose_name=_("Membership Remittance"))
    family = models.ForeignKey(to=Family, on_delete=CASCADE, verbose_name=_("Family"))
