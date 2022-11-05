from ampa_members_manager.academic_course.models.level import Level
from ampa_members_manager.family.models.membership import Membership
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.family.models.family import Family


class Statistic():

    @staticmethod
    def get_level_members_by_total(level):
        age = Level.get_age_by_level(level)
        
        members_count = Membership.objects.by_child_age(age).count()
        children_count = Child.objects.by_age(age).count()

        return f'{members_count}/{children_count}'
    
    @staticmethod
    def get_hh_members_by_total():
        min_age = Level.AGE_HH2
        max_age = Level.AGE_HH5
        members_count = Membership.objects.by_child_age_range(min_age, max_age).count()
        children_count = Child.objects.by_age_range(min_age, max_age).count()

        return f'{members_count}/{children_count}'
    
    @staticmethod
    def get_lh_members_by_total():
        min_age = Level.AGE_LH1
        max_age = Level.AGE_LH6
        members_count = Membership.objects.by_child_age_range(min_age, max_age).count()
        children_count = Child.objects.by_age_range(min_age, max_age).count()

        return f'{members_count}/{children_count}'

    def children_in_school():
        children_count = Child.objects.count()
        children_in_school_count = Child.objects.in_school().count()
        return f'{children_in_school_count}/{children_count}'
    
    def families_in_school():
        family_count = Family.objects.count()
        family_in_school_count = Family.objects.has_any_children().count()
        return f'{family_in_school_count}/{family_count}'