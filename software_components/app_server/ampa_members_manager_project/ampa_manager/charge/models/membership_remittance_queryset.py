from django.db.models.query import QuerySet
from django.utils import timezone

from ampa_manager.academic_course.models.academic_course import AcademicCourse


class MembershipRemittanceQuerySet(QuerySet):

    def paid_on_current_year(self) -> QuerySet:
        return self.filter(payment_date__year=timezone.now().year)

    def of_course(self, course: AcademicCourse):
        return self.filter(course=course)
