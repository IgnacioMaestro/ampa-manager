from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration_queryset import \
    AfterSchoolRegistrationQuerySet
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.membership import Membership
from ampa_manager.utils.utils import Utils


class AfterSchoolRegistration(models.Model):
    after_school_edition = models.ForeignKey(
        to=AfterSchoolEdition, on_delete=models.CASCADE, verbose_name=_("After-school edition"))
    child = models.ForeignKey(to=Child, on_delete=models.CASCADE, verbose_name=_("Child"))
    holder = models.ForeignKey(to=Holder, on_delete=models.CASCADE, verbose_name=_("Holder"))

    objects = Manager.from_queryset(AfterSchoolRegistrationQuerySet)()

    class Meta:
        verbose_name = _('After-school registration')
        verbose_name_plural = _('After-school registrations')
        db_table = 'after_school_registration'
        constraints = [
            models.UniqueConstraint(
                fields=['after_school_edition', 'child'], name='unique_after_school_edition_for_child'),
        ]

    def __str__(self) -> str:
        return f'{self.after_school_edition}, {self.child}'

    def clean(self):
        if not self.holder.parent.family_set.filter(id=self.child.family.id).exists():
            raise ValidationError(_('The selected bank account does not belong to the child\'s family'))

    def calculate_price(self) -> float:
        if Membership.is_member_child(self.child):
            return float(self.after_school_edition.price_for_member)
        else:
            return float(self.after_school_edition.price_for_no_member)

    def get_html_link(self) -> str:
        return Utils.get_model_link(AfterSchoolRegistration.__name__.lower(), self.id, str(self))
