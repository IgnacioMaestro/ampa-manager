from __future__ import annotations

from typing import List, Optional

from django.db import models
from django.db.models import SET_NULL, QuerySet, Manager
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from ampa_manager.academic_course.models.level import Level
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family_queryset import FamilyQuerySet
from ampa_manager.family.models.parent import Parent
from ampa_manager.management.commands.results.import_result import ImportResult
from ampa_manager.management.commands.results.processing_state import ProcessingState
from ampa_manager.utils.fields_formatters import FieldsFormatters
from ampa_manager.utils.string_utils import StringUtils


class Family(TimeStampedModel):
    surnames = models.CharField(max_length=500, verbose_name=_("Surnames"))
    decline_membership = models.BooleanField(
        default=False, verbose_name=_("Decline membership"), help_text=_(
            'It prevents the family from becoming a member. For example, if they no longer have children at school but you do not want to delete the record.'))
    parents = models.ManyToManyField(to=Parent, verbose_name=_("Parents"))
    default_bank_account = models.ForeignKey(
        to=BankAccount, on_delete=SET_NULL, null=True, blank=True, verbose_name=_("Default bank account"),
        help_text=_("Save the family to see its bank accounts"))
    is_defaulter = models.BooleanField(
        default=False, verbose_name=_("Defaulter"), help_text=_('Informative field only'))

    objects = Manager.from_queryset(FamilyQuerySet)()

    class Meta:
        verbose_name = _('Family')
        verbose_name_plural = _("Families")
        db_table = 'family'

    def __str__(self) -> str:
        return f'{self.surnames}'

    def get_parent_count(self):
        return self.parents.all().count()

    def get_children_count(self):
        return self.child_set.count()

    def get_children_in_school_count(self):
        return self.child_set.of_age_in_range(Level.AGE_HH2, Level.AGE_LH6).count()

    @classmethod
    def all_families(cls) -> QuerySet[Family]:
        return Family.objects.all()

    def clean_surnames(self):
        return FieldsFormatters.clean_name(self.cleaned_data['surnames'])

    def to_decline_membership(self):
        self.decline_membership = True
        self.save()

    def matches_surnames(self, surnames):
        return StringUtils.compare_ignoring_everything(self.surnames, surnames)

    def has_parent(self, parent_name_and_surnames):
        return self.find_parent(parent_name_and_surnames) is not None

    def find_parent(self, name_and_surnames: str) -> Optional[Parent]:
        if name_and_surnames:
            family_parents = self.parents.all()
            for parent in family_parents:
                if parent.matches_name_and_surnames(name_and_surnames, strict=True):
                    return parent
            for parent in family_parents:
                if parent.matches_name_and_surnames(name_and_surnames, strict=False):
                    return parent
        return None

    def find_child(self, name: str, exclude_id: Optional[int] = None) -> Optional[Child]:
        if name:
            family_children = Child.objects.with_family(self)
            for child in family_children:
                if exclude_id and child.id == exclude_id:
                    continue
                if child.matches_name(name, strict=True):
                    return child
            for child in family_children:
                if exclude_id and child.id == exclude_id:
                    continue
                if child.matches_name(name, strict=False):
                    return child
        return None

    @staticmethod
    def find(surnames: str, parents_name_and_surnames: Optional[List[str]] = None):
        family = None
        error = None

        families = Family.filter_by_surnames(surnames)

        if len(families) == 1:
            family = families[0]
        elif len(families) > 1:
            family = Family.get_family_filtered_by_parent(families, parents_name_and_surnames)
            if family is None:
                if parents_name_and_surnames:
                    parents = ', '.join(parents_name_and_surnames)
                else:
                    parents = ''
                error = f'Multiple families with surnames "{surnames}". Parents: "{parents}"'

        return family, error

    @staticmethod
    def get_family_filtered_by_parent(families: List[Family], parents_name_and_surnames: List[str]) -> Optional[Family]:
        if parents_name_and_surnames:
            for family in families:
                for parent_name_and_surnames in parents_name_and_surnames:
                    if family.has_parent(parent_name_and_surnames):
                        return family
        return None

    @staticmethod
    def fix_surnames():
        for family in Family.objects.all():
            fixed_surnames = FieldsFormatters.clean_name(family.surnames)
            if fixed_surnames != family.surnames:
                print(f'Family surnames fixed: "{family.surnames}" -> "{fixed_surnames}"')
                family.surnames = fixed_surnames
                family.save(update_fields=['surnames'])

    @staticmethod
    def remove_duplicated_children():
        for family in Family.objects.all():
            for child in Child.objects.with_family(family):
                duplicated = family.find_child(child.name, child.id)
                if duplicated:
                    print(f'\nDuplicated child: Family "{family.surnames}"')
                    print(f'- Kept: #{child.id}, {child.name}, {child.year_of_birth}, {child.repetition}, {child.family.id}')
                    print(f'- Removed: #{duplicated.id}, {duplicated.name}, {duplicated.year_of_birth}, {duplicated.repetition}, {duplicated.family.id}')
                    duplicated.delete()

    @staticmethod
    def filter_by_surnames(surnames) -> List[Family]:
        families = []
        for family in Family.objects.all():
            if family.matches_surnames(surnames):
                families.append(family)
        return families

    @staticmethod
    def review_data():
        warnings = []

        families_without_account = Family.objects.without_default_bank_account().count()
        if families_without_account > 0:
            warnings.append(f'- Families without bank account: {families_without_account}')

        families_with_more_than_2_parents = Family.objects.with_more_than_two_parents().count()
        if families_with_more_than_2_parents > 0:
            warnings.append(f'- Families with more than 2 parents: {families_with_more_than_2_parents}')

        return warnings

    @staticmethod
    def import_family(family_surnames: str, parent1_name_and_surnames: Optional[str] = None,
                      parent2_name_and_surnames: Optional[str] = None):
        family = None
        state = ProcessingState.NOT_PROCESSED
        error = None

        if family_surnames:
            parents_name_and_surnames = []
            if parent1_name_and_surnames:
                parents_name_and_surnames.append(parent1_name_and_surnames)
            if parent2_name_and_surnames:
                parents_name_and_surnames.append(parent2_name_and_surnames)

            family, error = Family.find(family_surnames, parents_name_and_surnames)

            if family:
                state = ProcessingState.NOT_MODIFIED
            elif error:
                state = ProcessingState.ERROR
            elif family_surnames:
                family = Family.objects.create(surnames=family_surnames)
                state = ProcessingState.CREATED
        else:
            state = ProcessingState.ERROR
            error = 'Missing surnames'

        return family, state, error

    @staticmethod
    def import_family(family_surnames: str, parent1_name_and_surnames: Optional[str] = None,
                      parent2_name_and_surnames: Optional[str] = None) -> ImportResult:
        result = ImportResult()

        if family_surnames:
            parents_name_and_surnames = []
            if parent1_name_and_surnames:
                parents_name_and_surnames.append(parent1_name_and_surnames)
            if parent2_name_and_surnames:
                parents_name_and_surnames.append(parent2_name_and_surnames)

            family, error = Family.find(family_surnames, parents_name_and_surnames)

            if family:
                result.set_not_modified(family)
            elif error:
                result.set_error(error)
            elif family_surnames:
                family = Family.objects.create(surnames=family_surnames)
                result.set_created(family)
        else:
            result.set_error('Missing surnames')

        return result
