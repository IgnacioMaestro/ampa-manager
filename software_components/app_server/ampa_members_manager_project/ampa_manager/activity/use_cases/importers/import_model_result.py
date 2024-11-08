from typing import Optional

from django.db.models import Model
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.templatetags.html_blocks import html_new_line_tab_hyphen


class ModifiedField:
    def __init__(self, field_name: str, value_before, value_after):
        self.field_name = field_name
        self.value_before = value_before
        self.value_after = value_after


class ImportModelResult:
    NOT_PROCESSED = 'NOT_PROCESSED'
    NOT_MODIFIED = 'NOT_MODIFIED'
    CREATED = 'CREATED'
    UPDATED = 'UPDATED'
    ERROR = 'ERROR'
    OMITTED = 'OMITTED'

    STATES_LABELS = {
        NOT_PROCESSED: _('Not processed'),
        NOT_MODIFIED: _('Not modified'),
        CREATED: _('Created'),
        UPDATED: _('Modified'),
        ERROR: _('Error'),
        OMITTED: _('Omitted'),
    }

    def __init__(self, model):
        self.model = model
        self.instance: Optional[Model] = None
        self.instance_str: Optional[str] = ''
        self.state: str = self.NOT_PROCESSED
        self.modified_fields: list[ModifiedField] = []
        self.error_message: Optional[str] = None
        self.warnings: list = []
        self.minor_warnings: list = []

    def __str__(self) -> str:
        return f'{self.model._meta.verbose_name}: {self.state}'

    def get_instance_details(self, instance: Model) -> str:
        if instance is not None:
            if self.model == CustodyRegistration:
                return (f'{html_new_line_tab_hyphen}{instance.assisted_days} {CustodyRegistration.ASSISTED_DAYS}'
                        f'{html_new_line_tab_hyphen}{instance.holder.bank_account} ({instance.holder.parent})')
            elif self.model == CampsRegistration:
                return f'{instance.holder}'
            elif self.model == AfterSchoolRegistration:
                return f'{instance.holder}'
            elif self.model == Child:
                return f'{instance.name} {str(instance.family.surnames)}, {instance.level}'
            elif self.model == Family:
                return f'{instance.surnames}'
            else:
                return str(instance)
        else:
            return ''

    def set_instance(self, instance):
        self.instance = instance
        self.instance_str = self.get_instance_details(instance)

    def set_not_modified(self, instance):
        self.set_instance(instance)
        self.state = self.NOT_MODIFIED

    def set_updated(self, instance, modified_fields: list[ModifiedField]):
        self.set_instance(instance)
        self.state = self.UPDATED
        self.modified_fields = modified_fields

    def set_error(self, error_message: str):
        self.state = self.ERROR
        self.instance = None
        self.error_message = error_message

    def set_created(self, instance):
        self.set_instance(instance)
        self.state = self.CREATED

    def set_omitted(self, instance=None, warning=None):
        self.set_instance(instance)
        self.state = self.OMITTED

        if warning:
            self.add_warning(warning)

    def add_warning(self, warning, minor: bool = False):
        if minor:
            self.minor_warnings.append(warning)
        else:
            self.warnings.append(warning)

    @property
    def success(self) -> bool:
        return self.state not in [self.ERROR]

    @property
    def error(self) -> bool:
        return self.state in [self.ERROR]

    @property
    def warning(self) -> bool:
        return len(self.warnings) > 0

    @property
    def model_verbose_name(self):
        return self.model._meta.verbose_name

    @property
    def state_label(self):
        return self.STATES_LABELS.get(self.state, self.state)

    @property
    def instance_url(self):
        if self.instance:
            return self.instance.get_absolute_url()
        return None
