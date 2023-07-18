from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from ampa_manager.family.models.child import Child
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.membership import Membership
from ampa_manager.utils.utils import Utils

from .camps_edition import CampsEdition
from .camps_registration_queryset import CampsRegistrationQuerySet


class CampsRegistration(models.Model):
    camps_edition = models.ForeignKey(to=CampsEdition, on_delete=models.CASCADE, verbose_name=_("Camps edition"))
    child = models.ForeignKey(to=Child, on_delete=models.CASCADE, verbose_name=_("Child"))
    holder = models.ForeignKey(to=Holder, on_delete=models.CASCADE, verbose_name=_("Holder"))

    objects = Manager.from_queryset(CampsRegistrationQuerySet)()

    class Meta:
        verbose_name = _('Camps registration')
        verbose_name_plural = _('Camps registrations')
        db_table = 'camps_registration'

        constraints = [
            models.UniqueConstraint(fields=['camps_edition', 'child'], name='unique_camps_edition_for_child'),
        ]

    def __str__(self):
        return f'{self.camps_edition}, {self.child}'

    def clean(self):
        if not self.holder.parent.family_set.filter(id=self.child.family.id).exists():
            raise ValidationError(_('The selected bank account does not belong to the child\'s family'))

    def calculate_price(self) -> float:
        if self.is_member:
            return float(self.camps_edition.price_for_member)
        else:
            return float(self.camps_edition.price_for_no_member)

    @property
    def is_member(self):
        return Membership.is_member_child(self.child)

    def get_html_link(self, id_as_link_text=False, new_tab=True) -> str:
        link_text = str(self.id) if id_as_link_text else str(self)
        return Utils.get_model_link(CampsRegistration.__name__.lower(), self.id, link_text, new_tab)
