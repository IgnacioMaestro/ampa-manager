from typing import Optional

from django.db.models import Model
from django.utils.translation import gettext_lazy as _


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
        UPDATED: _('Updated'),
        ERROR: _('Error'),
        OMITTED: _('Omitted'),
    }

    def __init__(self, model: Model):
        self.model = model
        self.instance: Optional[Model] = None
        self.state: str = self.NOT_PROCESSED
        self.values_before: list = []
        self.values_after: list = []
        self.error_message: Optional[str] = None
        self.warnings: list = []
        self.minor_warnings: list = []

    def __str__(self) -> str:
        return f'{self.model._meta.verbose_name}: {self.state}'

    def set_not_modified(self, instance):
        self.instance = instance
        self.state = self.NOT_MODIFIED

    def set_updated(self, instance, values_before: list, values_after: list):
        self.instance = instance
        self.state = self.UPDATED
        self.values_before = values_before
        self.values_after = values_after

    def set_error(self, error_message: str):
        self.state = self.ERROR
        self.instance = None
        self.error_message = error_message

    def set_created(self, instance):
        self.instance = instance
        self.state = self.CREATED

    def set_omitted(self, instance=None, warning=None):
        self.instance = instance
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
