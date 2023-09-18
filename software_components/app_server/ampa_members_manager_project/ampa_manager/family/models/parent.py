from typing import List

from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField

from ampa_manager.family.models.parent_queryset import ParentQuerySet
from ampa_manager.family.use_cases.importers.fields_changes import FieldsChanges
from ampa_manager.utils.fields_formatters import FieldsFormatters
from ampa_manager.utils.string_utils import StringUtils
from ampa_manager.utils.utils import Utils


class Parent(TimeStampedModel):
    name_and_surnames = models.CharField(max_length=500, verbose_name=_("Name and surnames"), unique=True)
    phone_number = PhoneNumberField(null=True, blank=True, verbose_name=_("Phone number"))
    additional_phone_number = PhoneNumberField(null=True, blank=True, verbose_name=_("Other phone"))
    email = models.EmailField(null=True, blank=True, verbose_name=_("Email"))

    objects = Manager.from_queryset(ParentQuerySet)()

    class Meta:
        verbose_name = _('Parent')
        verbose_name_plural = _("Parents")
        db_table = 'parent'

    def __str__(self) -> str:
        return f'{self.full_name} ({self.id})'

    @property
    def full_name(self) -> str:
        return str(self.name_and_surnames)

    @property
    def families_ids(self) -> List[int]:
        return [f.id for f in self.family_set.order_by('id')]

    def belong_to_family(self, family):
        return self.family_set.filter(surnames=family.surnames).exists()
    
    def clean_name_and_surnames(self):
        return FieldsFormatters.clean_name(self.cleaned_data['name_and_surnames'])

    def matches_name_and_surnames(self, name_and_surnames, strict=False):
        if name_and_surnames and self.name_and_surnames:
            if strict:
                if StringUtils.compare_ignoring_everything(self.name_and_surnames, name_and_surnames):
                    return True
            elif StringUtils.contains_any_word(self.name_and_surnames, name_and_surnames):
                return True
        return False

    def is_modified(self, phone_number, additional_phone_number, email):
        return self.phone_number != phone_number \
               or self.additional_phone_number != additional_phone_number \
               or self.email != email

    def update(self, phone_number, additional_phone_number, email, allow_reset=True) -> FieldsChanges:
        fields_before = [self.name_and_surnames, self.phone_number, self.additional_phone_number, self.email]
        not_reset_fields = []
        updated = False

        if phone_number is not None or allow_reset:
            self.phone_number = phone_number
            updated = True
        elif self.phone_number:
            not_reset_fields.append(self.phone_number)

        if additional_phone_number is not None or allow_reset:
            self.additional_phone_number = additional_phone_number
            updated = True
        elif self.additional_phone_number:
            not_reset_fields.append(self.additional_phone_number)

        if email is not None or allow_reset:
            self.email = email
            updated = True
        elif self.email:
            not_reset_fields.append(self.email)

        if updated:
            self.save()

        fields_after = [self.name_and_surnames, self.phone_number, self.additional_phone_number, self.email]

        return FieldsChanges(fields_before, fields_after, not_reset_fields)

    def get_html_link(self) -> str:
        return Utils.get_model_link(Parent.__name__.lower(), self.id, str(self))

    @staticmethod
    def fix_name_and_surnames():
        for parent in Parent.objects.all():
            fixed_name_and_surnames = FieldsFormatters.clean_name(parent.name_and_surnames)
            if fixed_name_and_surnames != parent.name_and_surnames:
                print(f'Parent name and surnames fixed: "{parent.name_and_surnames}" -> "{fixed_name_and_surnames}"')
                parent.name_and_surnames = fixed_name_and_surnames
                parent.save(update_fields=['name_and_surnames'])

    @staticmethod
    def review_data():
        warnings = []

        parents_without_family = Parent.objects.has_no_family().count()
        if parents_without_family > 0:
            warnings.append(f'- Parents without family: {parents_without_family}')

        parents_in_multiple_families = Parent.objects.has_multiple_families().count()
        if parents_in_multiple_families > 0:
            warnings.append(f'- Parents with multiple families: {parents_in_multiple_families}')

        parents_with_multiple_bank_accounts = Parent.objects.with_multiple_bank_accounts().count()
        if len(parents_with_multiple_bank_accounts) > 0:
            warnings.append(f'- Parents with multiple bank accounts: {parents_with_multiple_bank_accounts}')

        return warnings

    @staticmethod
    def find(name_and_surnames: str):
        if name_and_surnames:
            family_parents = Parent.objects.all()
            for parent in family_parents:
                if parent.matches_name_and_surnames(name_and_surnames, strict=True):
                    return parent
        return None
