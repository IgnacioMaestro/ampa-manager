from django.db.models.query import QuerySet

from ampa_manager.academic_course.models.academic_course import AcademicCourse


class AfterSchoolEditionQuerySet(QuerySet):

    def of_course(self, course: AcademicCourse):
        return self.filter(academic_course=course)

    def with_code(self, code: str):
        return self.filter(code=code)
