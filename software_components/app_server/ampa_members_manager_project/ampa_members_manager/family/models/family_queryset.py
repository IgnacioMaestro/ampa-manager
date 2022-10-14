from django.db.models.query import QuerySet
from django.db.models import F

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.academic_course.models.course_name import CourseName
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.academic_course.models.course_name import CourseName

class FamilyQuerySet(QuerySet):

    def has_any_children(self):
        return self.filter(id__in=FamilyQuerySet.get_member_families_ids())
    
    def has_no_children(self):
        return self.exclude(id__in=FamilyQuerySet.get_member_families_ids())
    
    def get_member_families_ids():
        active_course = ActiveCourse.load()
        childs_with_age = Child.objects.annotate(age=active_course.initial_year - F('year_of_birth') - F('repetition'))
        childs_distinct_families = childs_with_age.filter(age__range=(CourseName.AGE_HH2, CourseName.AGE_LH6))
        families_ids = [c.family.id for c in childs_distinct_families if c.family.id not in childs_distinct_families]
        return families_ids