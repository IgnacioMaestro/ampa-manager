from typing import Optional

from django.db.models import Model


class ImportModelResult:
    NOT_PROCESSED = 'NOT_PROCESSED'
    NOT_MODIFIED = 'NOT_MODIFIED'
    CREATED = 'CREATED'
    UPDATED = 'UPDATED'
    ERROR = 'ERROR'
    OMITTED = 'OMITTED'

    def __init__(self, model: Model):
        self.model = model
        self.instance: Optional[Model] = None
        self.state: str = self.NOT_PROCESSED
        self.values_before: list = []
        self.values_after: list = []
        self.error_message: Optional[str] = None
        self.warnings: list = []

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

    def add_warning(self, warning):
        self.warnings.append(warning)

    @property
    def success(self):
        return self.state not in [self.ERROR]

    @property
    def error(self):
        return self.state in [self.ERROR]

    @property
    def model_verbose_name(self):
        return self.model._meta.verbose_name
