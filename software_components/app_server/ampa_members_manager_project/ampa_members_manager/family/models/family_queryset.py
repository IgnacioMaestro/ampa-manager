from django.db.models.query import QuerySet

from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.academic_course.models.level import Level
from ampa_members_manager.family.models.child import Child


class FamilyQuerySet(QuerySet):

    def has_any_children(self):
        return self.filter(id__in=FamilyQuerySet.get_families_ids_with_school_children())

    def has_no_children(self):
        return self.exclude(id__in=FamilyQuerySet.get_families_ids_with_school_children())

    @classmethod
    def get_families_ids_with_school_children(cls):
        distinct_families_ids = []
        for child in Child.objects.by_age_range(Level.AGE_HH2, Level.AGE_LH6):
            if child.family.id not in distinct_families_ids:
                distinct_families_ids.append(child.family.id)
        return distinct_families_ids

    def with_bank_account(self):
        return self.exclude(default_bank_account__isnull=True)

    def members(self):
        return self.filter(membership__academic_course=ActiveCourse.load())

    def no_members(self):
        return self.exclude(membership__academic_course=ActiveCourse.load())

    def with_default_account(self):
        return self.exclude(default_bank_account=None)

    def without_default_account(self):
        return self.filter(default_bank_account=None)

    def by_surnames(self, surnames):
        return self.filter(surnames__iexact=surnames)
