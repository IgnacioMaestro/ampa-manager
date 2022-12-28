from __future__ import annotations

import re

from django.db import models
from django.db.models import SET_NULL, QuerySet, Manager
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.parent import Parent
from ampa_manager.family.models.family_queryset import FamilyQuerySet
from ampa_manager.academic_course.models.level import Level
from ampa_manager.management.commands.import_command.surnames import SURNAMES


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

    def clean(self):
        if self.surnames:
            self.surnames = self.surnames.title().strip()

    def to_decline_membership(self):
        self.decline_membership = True
        self.save()

    @staticmethod
    def find(surnames, parents_name_and_surnames=[]):
        family = None
        error = None

        families = Family.objects.with_surnames(surnames)

        if families.count() == 1:
            family = families[0]
        elif families.count() > 1:
            if len(parents_name_and_surnames) > 0:
                family = Family.get_family_filtered_by_parent(families, parents_name_and_surnames)
                if family is None:
                    parents = ', '.join(parents_name_and_surnames)
                    error = f'Multiple families with surnames "{surnames}". Parents: "{parents}"'
            else:
                error = f'Multiple families with surnames "{surnames}"'

        return family, error

    @staticmethod
    def get_family_filtered_by_parent(families, parents_name_and_surnames):
        for family in families.all():
            for parent in family.parents.all():
                for name in parents_name_and_surnames:
                    if name and (name in parent.name_and_surnames or parent.name_and_surnames in name):
                        return family
        return None

    @staticmethod
    def fix_accents():
        for family in Family.objects.all():
            for wrong, right in SURNAMES.items():
                pattern = rf'\b{wrong}\b'
                if re.search(pattern, family.surnames):
                    before = family.surnames
                    family.surnames = re.sub(pattern, right, family.surnames)
                    family.surnames.replace(wrong, right)
                    family.save(update_fields=['surnames'])
                    print(f'Family surnames fixed: {before} -> {family.surnames}')
