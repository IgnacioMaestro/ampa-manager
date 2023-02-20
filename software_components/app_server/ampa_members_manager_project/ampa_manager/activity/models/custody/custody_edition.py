from django.db import models
from django.db.models import CASCADE
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.level import Level
from ampa_manager.activity.models.custody.custody_edition_queryset import CustodyEditionQuerySet
from ampa_manager.activity.models.price_per_level import PricePerLevel
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.family.models.membership import Membership


class CustodyEdition(PricePerLevel):
    period = models.CharField(max_length=300, verbose_name=_("Period"))
    max_days_for_charge = models.PositiveIntegerField(verbose_name=_("Max days for charge"))
    academic_course = models.ForeignKey(to=AcademicCourse, on_delete=CASCADE, verbose_name=_("Academic course"))
    cycle = models.CharField(max_length=3, null=False, blank=False, choices=Level.CYCLES,
                             default=Level.ID_CYCLE_PRIMARY, verbose_name=_("Cycle"))
    cost = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Cost"))
    
    objects = Manager.from_queryset(CustodyEditionQuerySet)()

    class Meta:
        verbose_name = _('Custody edition')
        verbose_name_plural = _('Custody editions')
        db_table = 'custody_edition'
        constraints = [
            models.UniqueConstraint(
                fields=['academic_course', 'period', 'cycle'], name='unique_academic_course_with_period_and_cycle'),
        ]

    def __str__(self) -> str:
        return f'{self.academic_course}, {self.period}, {self.cycle}'
    
    @property
    def no_members_registrations_count(self):
        return CustodyRegistration.objects.of_edition(self).no_members().count()
    
    @property
    def members_registrations_count(self):
        return CustodyRegistration.objects.of_edition(self).members().count()

    def get_topped_assisted_days(self):
        members = 0
        non_members = 0
        for registration in CustodyRegistration.objects.of_edition(self):

            topped_assisted_days = registration.assisted_days
            if topped_assisted_days > self.max_days_for_charge:
                topped_assisted_days = self.max_days_for_charge

            if Membership.is_member_child(registration.child):
                members += topped_assisted_days
            else:
                non_members += topped_assisted_days

        return members, non_members
    
    def calculate_prices(self):
        members_assisted_days, non_members_assisted_days = self.get_topped_assisted_days()
        registrations_count = (settings.CUSTODY_NON_MEMBERS_PRICE_SURCHARGE * non_members_assisted_days) + members_assisted_days
        if self.cost > 0 and registrations_count > 0:
            self.price_for_member = self.cost / registrations_count
            self.price_for_non_member = self.price_for_member * settings.CUSTODY_NON_MEMBERS_PRICE_SURCHARGE
            self.save()
            return True
        return False
