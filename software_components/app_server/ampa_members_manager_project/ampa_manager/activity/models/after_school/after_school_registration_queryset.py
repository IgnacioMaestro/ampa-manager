from django.db.models.query import QuerySet

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.charge.models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.holder.holder import Holder


class AfterSchoolRegistrationQuerySet(QuerySet):

    def of_after_school_remittance(self, after_school_remittance: AfterSchoolRemittance):
        return self.filter(after_school_edition__after_school_remittance=after_school_remittance)

    def of_child(self, child: Child):
        return self.filter(child=child)

    def of_active_course(self):
        active_course: AcademicCourse = ActiveCourse.load()
        return self.filter(after_school_edition__academic_course=active_course)

    def of_academic_course(self, course: AcademicCourse):
        return self.filter(after_school_edition__academic_course=course)

    def of_previous_courses(self):
        active_course: AcademicCourse = ActiveCourse.load()
        return self.filter(after_school_edition__academic_course__initial_year__lt=active_course.initial_year)

    def of_holder(self, holder: Holder):
        return self.filter(holder=holder)

    def of_edition(self, after_school_edition: AfterSchoolEdition):
        return self.filter(after_school_edition=after_school_edition)
