from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.models import Count

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.academic_course.models.level import Level
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.child import Child
from ampa_manager.utils.string_utils import StringUtils


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

    def with_membership_holder(self):
        return self.exclude(membership_holder__isnull=True)

    def without_membership_holder(self):
        return self.filter(membership_holder__isnull=True)

    def with_custody_holder(self):
        return self.exclude(custody_holder__isnull=True)

    def without_custody_holder(self):
        return self.filter(custody_holder__isnull=True)

    def with_camps_holder(self):
        return self.exclude(camps_holder__isnull=True)

    def without_camps_holder(self):
        return self.filter(camps_holder__isnull=True)

    def with_after_school_holder(self):
        return self.exclude(after_school_holder__isnull=True)

    def without_after_school_holder(self):
        return self.filter(after_school_holder__isnull=True)

    def any_holder_missing(self):
        return self.filter(
            Q(membership_holder__isnull=True) | Q(custody_holder__isnull=True) |
            Q(camps_holder__isnull=True) | Q(after_school_holder__isnull=True))

    def all_holders_completed(self):
        return self.filter(
            membership_holder__isnull=False, custody_holder__isnull=False,
            camps_holder__isnull=False, after_school_holder__isnull=False)

    def members_in_course(self, academic_course: AcademicCourse):
        return self.filter(membership__academic_course=academic_course)

    def no_members_in_course(self, academic_course: AcademicCourse):
        return self.exclude(membership__academic_course=academic_course)

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

    def of_parent(self, parent):
        return self.filter(parents=parent)

    def with_email(self):
        return self.exclude(Q(email__isnull=True) | Q(email=''))

    def without_email(self):
        return self.filter(Q(email__isnull=True) | Q(email=''))

    def with_this_email(self, email):
        return self.filter(Q(email=email) | Q(secondary_email=email))

    def with_these_surnames(self, surnames):
        return self.filter(normalized_surnames=StringUtils.normalize(str(surnames)))

    def possible_duplicated(self):
        duplicated_ids = []
        for account in BankAccount.objects.all():
            families_ids = list(set(self.filter(parents__holder__bank_account=account).values_list('id', flat=True)))
            if len(families_ids) > 1:
                duplicated_ids.extend(families_ids)
        return self.filter(id__in=duplicated_ids)
