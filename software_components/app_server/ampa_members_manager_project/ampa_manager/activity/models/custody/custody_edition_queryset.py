from django.db.models.query import QuerySet

from ampa_manager.academic_course.models.active_course import ActiveCourse


class CustodyEditionQuerySet(QuerySet):

    def with_remittance(self):
        return self.all()

    def without_remittance(self):
        return self.all()

    def of_current_academic_course(self):
        return self.filter(academic_course=ActiveCourse.load())

    def of_previous_academic_courses(self):
        return self.filter(academic_course__initial_year__lt=ActiveCourse.load().initial_year)
