from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.academic_course.models.level import Level
from ampa_members_manager.family.models.membership import Membership
from ampa_members_manager.family.models.child import Child


class Statistic():

    @staticmethod
    def get_course_members_by_total(level):
        age = Level.get_age_by_level(level)
        
        course_members_count = Membership.objects.by_child_age(age).count()
        course_child_count = Child.objects.by_age(age).count()

        return f'{course_members_count}/{course_child_count}'
