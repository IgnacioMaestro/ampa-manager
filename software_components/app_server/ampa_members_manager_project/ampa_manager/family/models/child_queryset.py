from django.db.models.query import QuerySet
from django.db.models import F

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.academic_course.models.level import Level


class ChildQuerySet(QuerySet):

    def of_age(self, age):
        return self.of_age_in_range(age, age)

    def in_school(self):
        return self.of_age_in_range(Level.AGE_HH2, Level.AGE_LH6)

    def in_school_of_family(self, family):
        return self.of_age_in_range(Level.AGE_HH2, Level.AGE_LH6).filter(family=family)

    def in_primary(self):
        return self.of_age_in_range(Level.AGE_LH1, Level.AGE_LH6)

    def in_pre_school(self):
        return self.of_age_in_range(Level.AGE_HH2, Level.AGE_HH5)

    def of_age_in_range(self, min_age, max_age):
        active_course = ActiveCourse.load()
        children_with_age = self.annotate(child_age=active_course.initial_year - F('year_of_birth') - F('repetition'))
        return children_with_age.filter(child_age__range=(min_age, max_age))

    def out_of_school(self):
        active_course = ActiveCourse.load()
        children_with_age = self.annotate(child_age=active_course.initial_year - F('year_of_birth') - F('repetition'))
        return children_with_age.exclude(child_age__range=(Level.AGE_HH2, Level.AGE_LH6))

    def with_name_and_of_family(self, name, family):
        return self.filter(name__iexact=name, family=family)

    def with_name_and_of_family_excluding_id(self, name, family, id_to_exclude):
        return self.filter(name__iexact=name, family=family).exclude(id=id_to_exclude)

    def with_family(self, family):
        return self.filter(family=family)

    def with_family_excluding_id(self, family, id_to_exclude):
        return self.filter(family=family).exclude(id=id_to_exclude)
