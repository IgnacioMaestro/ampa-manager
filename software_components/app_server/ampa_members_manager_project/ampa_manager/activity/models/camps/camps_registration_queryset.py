from django.db.models import F
from django.db.models.query import QuerySet

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from ampa_manager.charge.models.camps.camps_remittance import CampsRemittance
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.academic_course.models.active_course import ActiveCourse


class CampsRegistrationQuerySet(QuerySet):

    def of_camps_remittance(self, camps_remittance: CampsRemittance):
        return self.filter(camps_edition__camps_remittance=camps_remittance)

    def of_child(self, child: Child):
        return self.filter(child=child)

    def of_academic_course(self, course: AcademicCourse):
        return self.filter(camps_edition__academic_course=course)

    def of_holder(self, holder: Holder):
        return self.filter(holder=holder)

    def of_edition(self, camps_edition: CampsEdition):
        return self.filter(camps_edition=camps_edition)

    def members(self):
        return self.filter(child__family__membership__academic_course=ActiveCourse.load())

    def no_members(self):
        return self.exclude(child__family__membership__academic_course=ActiveCourse.load())

    def child_of_age(self, age):
        return self.child_age_in_range(age, age)

    def child_age_in_range(self, min_age, max_age):
        active_course = ActiveCourse.load()
        children_with_age = self.annotate(child_age=active_course.initial_year - F('child__year_of_birth') - F('child__repetition'))
        return children_with_age.filter(child_age__range=(min_age, max_age))
