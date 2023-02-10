from django.db import models
from django.db.models import CASCADE
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.activity.models.custody.custody_edition_queryset import CustodyEditionQuerySet
from ampa_manager.activity.models.price_per_level import PricePerLevel


class CustodyEdition(PricePerLevel):
    CYCLES = [
        (1, _('Pre-school')),
        (2, _('Primary education')),
    ]

    period = models.CharField(max_length=300, verbose_name=_("Period"))
    max_days_for_charge = models.PositiveIntegerField(verbose_name=_("Max days for charge"))
    academic_course = models.ForeignKey(to=AcademicCourse, on_delete=CASCADE, verbose_name=_("Academic course"))
    cycle = models.IntegerField(null=False, blank=False, choices=CYCLES, verbose_name=_("Cycle"))

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
