from django.db.models import F
from django.db.models.query import QuerySet

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.charge.models.custody.custody_remittance import CustodyRemittance
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.academic_course.models.active_course import ActiveCourse


class CustodyRegistrationQuerySet(QuerySet):

    def of_custody_remittance(self, custody_remittance: CustodyRemittance):
        return self.filter(custody_edition__custody_remittance=custody_remittance)

    def of_child(self, child: Child):
        return self.filter(child=child)

    def of_family(self, family: Family):
        return self.filter(child__family=family)

    def of_active_course(self):
        active_course: AcademicCourse = ActiveCourse.load()
        return self.filter(custody_edition__academic_course=active_course)

    def of_academic_course(self, course: AcademicCourse):
        return self.filter(custody_edition__academic_course=course)

    def of_previous_courses(self):
        active_course: AcademicCourse = ActiveCourse.load()
        return self.filter(custody_edition__academic_course__initial_year__lt=active_course.initial_year)

    def of_holder(self, holder: Holder):
        return self.filter(holder=holder)

    def of_edition(self, custody_edition: CustodyEdition):
        return self.filter(custody_edition=custody_edition)

    def members_in_course(self, academic_course: AcademicCourse):
        return self.filter(child__family__membership__academic_course=academic_course)

    def no_members_in_course(self, academic_course: AcademicCourse):
        return self.exclude(child__family__membership__academic_course=academic_course)

    def child_of_age(self, age):
        return self.child_age_in_range(age, age)

    def child_age_in_range(self, min_age, max_age):
        active_course = ActiveCourse.load()
        children_with_age = self.annotate(
            child_age=active_course.initial_year - F('child__year_of_birth') - F('child__repetition'))
        return children_with_age.filter(child_age__range=(min_age, max_age))
