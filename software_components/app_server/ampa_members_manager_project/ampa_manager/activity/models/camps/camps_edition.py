from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.models.academic_course import AcademicCourse


class CampsEdition(models.Model):
    academic_course = models.ForeignKey(to=AcademicCourse, on_delete=CASCADE, verbose_name=_("Academic course"))
    levels = models.CharField(max_length=300, verbose_name=_("Levels"))
    price_for_member = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Price for members"))
    price_for_no_member = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Price for no members"))

    class Meta:
        verbose_name = _('Camps edition')
        verbose_name_plural = _('Camps editions')
        db_table = 'camps_edition'
        constraints = [
            models.UniqueConstraint(fields=['academic_course', 'levels'], name='unique_academic_course_with_levels'),
        ]
