from django.db.models.query import QuerySet

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.family.models.child import Child

class MembershipQuerySet(QuerySet):

    def by_child_age(self, age):
        return self.by_child_age_range(age, age)
    
    def by_child_age_range(self, min_age, max_age):
        children_ids = Child.get_ids_by_age(min_age, max_age)
        return self.filter(academic_course=ActiveCourse.load(), family__child__id__in=children_ids)

    def active_course_members(self):
        return self.filter(academic_course=ActiveCourse.load())

    def by_family(self, family):
        return self.filter(family=family, academic_course=ActiveCourse.load())

    def by_parent(self, parent):
        families = [f.id for f in parent.family_set.all()]
        return self.filter(family__in=families, academic_course=ActiveCourse.load())
