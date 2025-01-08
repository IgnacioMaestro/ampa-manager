from __future__ import annotations

import decimal
import math

from django.db import models
from django.db.models import CASCADE, QuerySet
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.academic_course.models.level import Level
from ampa_manager.activity.models.custody.custody_edition_queryset import CustodyEditionQuerySet
from ampa_manager.activity.models.price_per_level import PricePerLevel
from ampa_manager.dynamic_settings.dynamic_settings import DynamicSetting


class CustodyEdition(PricePerLevel):
    period = models.CharField(max_length=300, verbose_name=_("Period"))
    days_with_service = models.PositiveIntegerField(verbose_name=_("Days with service"), default=30,
                                                    help_text=_('Days in which there was custody this edition'))
    academic_course = models.ForeignKey(to=AcademicCourse, on_delete=CASCADE, verbose_name=_("Academic course"))
    cycle = models.CharField(max_length=3, null=False, blank=False, choices=Level.CYCLES,
                             default=Level.ID_CYCLE_PRIMARY, verbose_name=_("Cycle"))
    cost = models.DecimalField(max_digits=6, decimal_places=2, null=True, verbose_name=_("Cost"),
                               help_text=_(
                                   'Prices can be automatically calculated with the action "Calculate prices" based on '
                                   'this cost and assisted days. No members have a surcharge'))

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
        return f'{self.academic_course}, {self.period}, {self.get_cycle_display()}'

    def str_short(self) -> str:
        return f'{self.academic_course}, {self.period}, {self.get_cycle_display()}'

    @property
    def no_members_registrations_count(self):
        active_course = ActiveCourse.load()
        return self.registrations.no_members_in_course(active_course).count()

    @property
    def members_registrations_count(self):
        active_course = ActiveCourse.load()
        return self.registrations.members_in_course(active_course).count()

    @property
    def registrations_count(self):
        return self.registrations.count()

    @property
    def charged(self):
        charged_members = self.price_for_member * self.get_assisted_days(members=True, topped=True)
        charged_no_members = self.price_for_no_member * self.get_assisted_days(members=False, topped=True)
        charged = charged_members + charged_no_members
        return charged

    @property
    def max_days_for_charge(self) -> int:
        return math.ceil(self.days_with_service * (DynamicSetting.load().custody_max_days_to_charge_percent / 100.0))

    def get_assisted_days(self, members=False, topped=False):
        assisted_days = 0

        active_course = ActiveCourse.load()
        if members:
            registrations = self.registrations.members_in_course(active_course)
        else:
            registrations = self.registrations.no_members_in_course(active_course)

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

    @classmethod
    def calculate_prices_from_multiple_editions(cls, editions: QuerySet[CustodyEdition]) -> bool:
        non_members_surcharge = cls.get_non_members_surcharge()

        total_assisted_days_members, total_assisted_days_non_members, total_cost = cls.get_editions_totals(editions)
        total_assisted_days = decimal.Decimal(
            (total_assisted_days_non_members * non_members_surcharge) + total_assisted_days_members)

        margin = decimal.Decimal(0.02)
        if total_cost and total_assisted_days:
            price_for_member = round(total_cost / total_assisted_days, 2) + margin
            price_for_no_member = round(price_for_member * non_members_surcharge, 2) + margin
            cls.update_editions_prices(price_for_member, price_for_no_member, editions)
            return True
        return False

    @classmethod
    def get_editions_totals(cls, editions: QuerySet[CustodyEdition]) -> (
            decimal.Decimal, decimal.Decimal, decimal.Decimal):
        total_assisted_days_members = 0
        total_assisted_days_non_members = 0
        total_cost = 0

        for edition in editions:
            total_assisted_days_members += edition.get_assisted_days(members=True, topped=True)
            total_assisted_days_non_members += edition.get_assisted_days(members=False, topped=True)
            total_cost += edition.cost

        return total_assisted_days_members, total_assisted_days_non_members, total_cost

    @classmethod
    def update_editions_prices(cls, price_for_member: decimal.Decimal, price_for_no_member: decimal.Decimal,
                               editions: QuerySet[CustodyEdition]):
        for edition in editions:
            edition.price_for_member = price_for_member
            edition.price_for_no_member = price_for_no_member
            edition.save()

    @classmethod
    def get_non_members_surcharge(cls) -> decimal.Decimal:
        return decimal.Decimal((DynamicSetting.load().custody_members_discount_percent + 100) / 100)

    @classmethod
    def are_ready_to_calculate_prices(cls, editions: QuerySet[CustodyEdition]) -> bool:
        for edition in editions:
            if not edition.is_ready_to_calculate_prices:
                return False
        return True

    def is_ready_to_calculate_prices(self):
        return (self.cost is not None and self.cost > 0
                and self.days_with_service is not None and self.days_with_service > 0
                and self.registrations.count() > 0)
