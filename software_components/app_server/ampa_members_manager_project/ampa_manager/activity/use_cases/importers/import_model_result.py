from typing import Optional

from django.db.models import Model


class ImportModelResult:
    NOT_PROCESSED = 0
    NOT_MODIFIED = 1
    CREATED = 2
    UPDATED = 3
    ERROR = 4

    def __init__(self, class_name: str):
        self.class_name = class_name
        self.instance: Optional[Model] = None
        self.state: int = self.NOT_PROCESSED
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

    def add_warning(self, warning):
        self.warnings.append(warning)

    @property
    def success(self):
        return self.state not in [self.ERROR]

    @property
    def error(self):
        return self.state in [self.ERROR]
