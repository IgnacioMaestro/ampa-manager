from __future__ import annotations

from typing import List, Optional

from django.db import models
from django.db.models import SET_NULL, QuerySet, Manager
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from ampa_manager.academic_course.models.level import Level
from ampa_manager.utils.fields_formatters import FieldsFormatters
from ampa_manager.utils.string_utils import StringUtils
from .child import Child
from .family_queryset import FamilyQuerySet
from .holder.holder import Holder
from .parent import Parent
from ...utils.utils import Utils


class Family(TimeStampedModel):
    HOLDER_HELP_TEXT = _("Save the family to see its bank accounts")
    DECLINE_MEMBERSHIP_HELP_TEXT = _(
        "The family does not want to renew the membesrhip next year. It makes no change this year")
    surnames = models.CharField(max_length=500, verbose_name=_("Surnames"))
    normalized_surnames = models.CharField(max_length=500, verbose_name=_("Normalized surnames"), blank=True)
    decline_membership = models.BooleanField(
        default=False, verbose_name=_("Decline membership"), help_text=DECLINE_MEMBERSHIP_HELP_TEXT)
    parents = models.ManyToManyField(to=Parent, verbose_name=_("Parents"))
    membership_holder = models.ForeignKey(
        to=Holder, on_delete=SET_NULL, null=True, blank=True, verbose_name=_("Membership holder"),
        help_text=HOLDER_HELP_TEXT + '. ' + _("This account will be used if no other is specified"))
    custody_holder = models.ForeignKey(
        to=Holder, on_delete=SET_NULL, null=True, blank=True, verbose_name=_("Custody holder"),
        help_text=HOLDER_HELP_TEXT, related_name='custody_holder')
    after_school_holder = models.ForeignKey(
        to=Holder, on_delete=SET_NULL, null=True, blank=True, verbose_name=_("After-school holder"),
        help_text=HOLDER_HELP_TEXT, related_name='after_school_holder')
    camps_holder = models.ForeignKey(
        to=Holder, on_delete=SET_NULL, null=True, blank=True, verbose_name=_("Camps holder"),
        help_text=HOLDER_HELP_TEXT, related_name='camps_holder')
    is_defaulter = models.BooleanField(
        default=False, verbose_name=_("Defaulter"), help_text=_('Informative field only'))
    email = models.EmailField(null=True, blank=True, verbose_name=_("Email"))
    secondary_email = models.EmailField(null=True, blank=True, verbose_name=_("Secondary email"))

    objects = Manager.from_queryset(FamilyQuerySet)()

    class Meta:
        verbose_name = _('Family')
        verbose_name_plural = _("Families")
        db_table = 'family'

    def __str__(self) -> str:
        children_names = self.children_names
        if not children_names or children_names == '':
            children_names = _('No children')
        return f'{self.surnames}: {self.parents_names} ({children_names})'

    def save(self, *args, **kwargs):
        self.normalize_fields()
        super(Family, self).save(*args, **kwargs)

    def normalize_fields(self):
        self.normalized_surnames = StringUtils.normalize(str(self.surnames))

    @property
    def children_names(self) -> str:
        return ', '.join(c.name for c in self.child_set.all())

    @property
    def parents_names(self) -> str:
        names = []
        for parent in self.parents.all():
            names.append(parent.name_and_surnames)
        return ', '.join(names)

    def get_parent_count(self) -> int:
        return self.parents.all().count()

    def get_children_count(self) -> int:
        return self.child_set.count()

    def get_children_in_school_count(self) -> int:
        return self.child_set.of_age_in_range(Level.AGE_HH2, Level.AGE_LH6).count()

    @classmethod
    def all_families(cls) -> QuerySet[Family]:
        return Family.objects.all()

    def clean_surnames(self):
        return FieldsFormatters.format_name(self.cleaned_data['surnames'])

    def to_decline_membership(self):
        self.decline_membership = True
        self.save()

    def get_html_link(self, print_parents=False, print_children=False, print_id=False) -> str:
        link_text = str(self)
        if print_id:
            link_text += f' ({self.id})'
        if print_parents:
            parents_names = [p.full_name for p in self.parents.all()]
            link_text += '. <b>Padres</b>: ' + ', '.join(parents_names)
        if print_children:
            children_names = [c.name for c in self.child_set.all()]
            link_text += '. <b>Hijos</b>: ' + ', '.join(children_names)

        return Utils.get_model_instance_link(Family.__name__.lower(), self.id, link_text)

    def get_children_names_csv(self):
        return ', '.join([c.name for c in self.child_set.all()])

    def get_similar_names_families(self):
        similar_families = []
        similar_ids = []
        for family in Family.objects.exclude(id=self.id).order_by('surnames'):
            for normalized_surname_word in StringUtils.normalize(self.surnames).split(' '):
                if normalized_surname_word not in StringUtils.SURNAMES_IGNORE_WORDS:
                    if normalized_surname_word in StringUtils.normalize(family.surnames):
                        if family.id not in similar_ids:
                            similar_families.append(family)
                            similar_ids.append(family.id)
        return similar_families

    def get_emails(self, parents_emails=True, family_emails=True) -> List[str]:
        emails = []
        if parents_emails:
            for parent in self.parents.all():
                if parent.email and parent.email not in emails:
                    emails.append(parent.email)
        if family_emails:
            if self.email and self.email not in emails:
                emails.append(self.email)
            if self.secondary_email and self.secondary_email not in emails:
                emails.append(self.secondary_email)
        return emails

    def update_email(self, email: str):
        if not self.email:
            self.email = email
        else:
            self.secondary_email = email
        self.save()

    def email_matches(self, email: str) -> bool:
        return email in [self.email, self.secondary_email]

    def update_custody_holder(self, holder: Holder):
        if self.custody_holder != holder:
            self.custody_holder = holder
            self.save()

    def update_membership_holder(self, holder: Holder):
        if self.membership_holder != holder:
            self.membership_holder = holder
            self.save()

    def update_camps_holder(self, holder: Holder):
        if self.camps_holder != holder:
            self.camps_holder = holder
            self.save()

    def update_after_school_holder(self, holder: Holder):
        if self.after_school_holder != holder:
            self.after_school_holder = holder
            self.save()

    @staticmethod
    def get_families_parents_emails(families: QuerySet[Family], parents_emails=True, family_emails=True) -> List[str]:
        emails = []
        for family in families:
            emails.extend(family.get_emails(parents_emails, family_emails))
        return emails

    @staticmethod
    def get_family_filtered_by_child(families: List[Family], child_name: str) -> Optional[Family]:
        if child_name:
            for family in families:
                for child in family.child_set.all():
                    if StringUtils.compare_ignoring_everything(child.name, child_name):
                        return family
        return None

    @staticmethod
    def fix_surnames():
        for family in Family.objects.all():
            fixed_surnames = FieldsFormatters.format_name(family.surnames)
            if fixed_surnames != family.surnames:
                print(f'Family surnames fixed: "{family.surnames}" -> "{fixed_surnames}"')
                family.surnames = fixed_surnames
                family.save(update_fields=['surnames'])

    @staticmethod
    def get_duplicated_families():
        duplicated = []
        processed = []
        for family1 in Family.objects.all():
            if family1.id not in processed:
                for family2 in Family.objects.exclude(id=family1.id):
                    if StringUtils.compare_ignoring_everything(family1.surnames, family2.surnames):
                        duplicated.append([family1, family2])
                        processed.extend([family1.id, family2.id])
        return duplicated

    @staticmethod
    def get_duplicated_parents():
        duplicated = []
        processed = []
        for family in Family.objects.all():
            for parent1 in family.parents.all():
                if parent1.id not in processed:
                    for parent2 in family.parents.exclude(id=parent1.id):
                        if StringUtils.compare_ignoring_everything(
                                parent1.name_and_surnames, parent2.name_and_surnames):
                            duplicated.append([parent1, parent2])
                            processed.extend([parent1.id, parent2.id])
        return duplicated

    @staticmethod
    def get_duplicated_children():
        duplicated = []
        processed = []
        for family in Family.objects.all():
            for child1 in Child.objects.with_family(family):
                if child1.id not in processed:
                    for child2 in Child.objects.with_family(family).exclude(id=child1.id):
                        if StringUtils.compare_ignoring_everything(child1.name, child2.name):
                            duplicated.append([child1, child2])
                            processed.extend([child1.id, child2.id])
        return duplicated

    @staticmethod
    def review_data():
        warnings = []

        families_without_account = Family.objects.without_membership_holder().count()
        if families_without_account > 0:
            warnings.append(f'- Families without bank account: {families_without_account}')

        families_with_more_than_2_parents = Family.objects.with_more_than_two_parents().count()
        if families_with_more_than_2_parents > 0:
            warnings.append(f'- Families with more than 2 parents: {families_with_more_than_2_parents}')

        return warnings
