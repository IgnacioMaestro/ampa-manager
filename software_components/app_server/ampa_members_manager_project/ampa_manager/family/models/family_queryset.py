from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.models import Count

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.academic_course.models.level import Level
from ampa_manager.family.models.child import Child


class FamilyQuerySet(QuerySet):

    def has_any_children(self):
        return self.filter(id__in=FamilyQuerySet.get_families_ids_with_school_children())

    def has_no_children(self):
        return self.exclude(id__in=FamilyQuerySet.get_families_ids_with_school_children())

    @classmethod
    def get_families_ids_with_school_children(cls):
        distinct_families_ids = []
        for child in Child.objects.of_age_in_range(Level.AGE_HH2, Level.AGE_LH6):
            if child.family.id not in distinct_families_ids:
                distinct_families_ids.append(child.family.id)
        return distinct_families_ids

    def with_default_bank_account(self):
        return self.exclude(default_bank_account__isnull=True)

    def without_default_bank_account(self):
        return self.filter(default_bank_account__isnull=True)

    def members(self):
        return self.filter(membership__academic_course=ActiveCourse.load())

    def no_members(self):
        return self.exclude(membership__academic_course=ActiveCourse.load())

    def with_surnames(self, surnames):
        return self.filter(surnames__iexact=surnames)
    
    def with_number_of_parents(self, number):
        self = self.annotate(parents_count=Count('parents'))
        return self.filter(parents_count=number)
    
    def with_more_than_two_parents(self):
        self = self.annotate(parents_count=Count('parents'))
        return self.filter(parents_count__gt=2)

    def no_declined_membership(self) -> QuerySet:
        return self.filter(decline_membership=False)

    def not_included_in_receipt_of_course(self, academic_course: AcademicCourse):
        return self.filter(
            Q(membershipreceipt__isnull=True) | ~Q(membershipreceipt__remittance__course=academic_course))