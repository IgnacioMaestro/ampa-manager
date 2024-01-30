import decimal

from django.conf import settings
from django.db import models
from django.db.models import CASCADE
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.level import Level
from ampa_manager.activity.models.custody.custody_edition_queryset import CustodyEditionQuerySet
from ampa_manager.activity.models.price_per_level import PricePerLevel
from ampa_manager.dynamic_settings.dynamic_settings import DynamicSetting


class CustodyEdition(PricePerLevel):
    period = models.CharField(max_length=300, verbose_name=_("Period"))
    max_days_for_charge = models.PositiveIntegerField(verbose_name=_("Max days for charge"))
    academic_course = models.ForeignKey(to=AcademicCourse, on_delete=CASCADE, verbose_name=_("Academic course"))
    cycle = models.CharField(max_length=3, null=False, blank=False, choices=Level.CYCLES,
                             default=Level.ID_CYCLE_PRIMARY, verbose_name=_("Cycle"))
    cost = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_("Cost"),
                               help_text=_(
                                   'Prices can be automatically calculated with the action "Calculate prices" based on '
                                   'this cost and assisted days. No members have a surcharge of %(surcharge)s ') %
                                         {'surcharge': f'{DynamicSetting.load().custody_members_discount_percent}%'})

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
        return (f'{self.academic_course}, {self.period}, {self.get_cycle_display()}, {self.registrations_count} '
                f'{_("registrations")}')
    
    @property
    def no_members_registrations_count(self):
        return self.registrations.no_members().count()

    @property
    def members_registrations_count(self):
        return self.registrations.members().count()

    @property
    def registrations_count(self):
        return self.registrations.count()

    @property
    def charged(self):
        charged_members = self.price_for_member * self.get_assisted_days(members=True, topped=True)
        charged_no_members = self.price_for_no_member * self.get_assisted_days(members=False, topped=True)
        charged = charged_members + charged_no_members
        return charged

    def get_assisted_days(self, members=False, topped=False):
        assisted_days = 0

        if members:
            registrations = self.registrations.members()
        else:
            registrations = self.registrations.no_members()

        for registration in registrations:

            registration_assisted_days = registration.assisted_days
            if topped and registration_assisted_days > self.max_days_for_charge:
                registration_assisted_days = self.max_days_for_charge

            assisted_days += registration_assisted_days

        return assisted_days
    
    def calculate_prices(self):
        members_assisted_days = self.get_assisted_days(members=True, topped=True)
        non_members_assisted_days = self.get_assisted_days(members=False, topped=True)
        non_members_surcharge = decimal.Decimal((DynamicSetting.load().custody_members_discount_percent + 100) / 100)

        assisted_days = decimal.Decimal((non_members_assisted_days * non_members_surcharge) + members_assisted_days)
        if self.cost and assisted_days:
            self.price_for_member = self.cost / assisted_days
            self.price_for_no_member = self.price_for_member * non_members_surcharge
            self.save()
            return True
        return False
