from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField

from ampa_manager.family.models.parent_queryset import ParentQuerySet
from ampa_manager.field_formatters.fields_formatter import FieldsFormatter
from ampa_manager.utils.string_utils import StringUtils


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
        return self.full_name

    @property
    def full_name(self) -> str:
        return str(self.name_and_surnames)

    def belong_to_family(self, family):
        return self.family_set.filter(surnames=family.surnames).exists()
    
    def clean_name_and_surnames(self):
        return FieldsFormatter.clean_name(self.cleaned_data['name_and_surnames'])

    def matches_name_and_surnames(self, name_and_surnames, strict=False):
        if name_and_surnames and self.name_and_surnames:
            if strict:
                if StringUtils.compare_ignoring_everything(self.name_and_surnames, name_and_surnames):
                    return True
            elif StringUtils.contains_any_word(self.name_and_surnames, name_and_surnames):
                return True
        return False

    @staticmethod
    def fix_name_and_surnames():
        for parent in Parent.objects.all():
            fixed_name_and_surnames = FieldsFormatter.clean_name(parent.name_and_surnames)
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
