from django.db.models.query import QuerySet

from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.family.models.child import Child


class MembershipQuerySet(QuerySet):

    def of_child_with_age(self, age):
        return self.of_child_in_age_range(age, age)

    def of_child_in_age_range(self, min_age, max_age):
        children_ids = Child.get_children_ids(min_age, max_age)
        return self.filter(academic_course=ActiveCourse.load(), family__child__id__in=children_ids)

    def of_active_course(self):
        return self.filter(academic_course=ActiveCourse.load())

    def of_family(self, family):
        return self.filter(family=family, academic_course=ActiveCourse.load())

    def of_parent(self, parent):
        families = [f.id for f in parent.family_set.all()]
        return self.filter(family__in=families, academic_course=ActiveCourse.load())
