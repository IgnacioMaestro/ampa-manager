from django.db.models.query import QuerySet
from django.db.models import F

from ampa_members_manager.academic_course.models.active_course import ActiveCourse

class ChildQuerySet(QuerySet):

    def by_age(self, age):
        return self.by_age_range(age, age)

    def by_age_range(self, min_age, max_age):
        active_course = ActiveCourse.load()
        childs_with_age = self.annotate(age=active_course.initial_year - F('year_of_birth') - F('repetition'))
        return childs_with_age.filter(age__range=(min_age, max_age))
