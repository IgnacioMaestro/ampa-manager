from django.db.models.query import QuerySet
from django.db.models import F

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.academic_course.models.course_name import CourseName
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.academic_course.models.course_name import CourseName

class FamilyQuerySet(QuerySet):

    def has_any_children(self):
        return self.filter(id__in=FamilyQuerySet.get_families_with_school_children_ids())
    
    def has_no_children(self):
        return self.exclude(id__in=FamilyQuerySet.get_families_with_school_children_ids())
    
    def get_families_with_school_children_ids():
        distinct_families_ids = []
        for child in Child.objects.age_range(CourseName.AGE_HH2, CourseName.AGE_LH6):
            if child.family.id not in distinct_families_ids:
                distinct_families_ids.append(child.family.id)
        return distinct_families_ids
