from typing import Optional, List

from django.db.models import Model

from ampa_manager.family.use_cases.importers.fields_changes import FieldsChanges
from ampa_manager.utils.processing_state import ProcessingState


class ImportModelResult:

    def __init__(self, class_name, excel_fields):
        self.class_name: str = class_name
        self.imported_object: Optional[Model] = None
        self.state: ProcessingState = ProcessingState.NOT_PROCESSED
        self.state2: Optional[ProcessingState] = None
        self.error: Optional[str] = None
        self.excel_fields: List = excel_fields
        self.fields_before: List = []
        self.fields_after: List = []
        self.not_reset_fields: List = []

    def __str__(self):
        changes = ''
        changed_fields = self.get_changed_fields()
        if changed_fields:
            changes += f'Changes: {changed_fields}.'

        error = ''
        if self.error:
            error += f'. Error: {self.error}.'

        excel_fields = self.get_excel_fields_csv()

        return f'{self.class_name} ({self.object_id}): {excel_fields} -> {self.states_names}. {changes} {error}'

    @property
    def states_names(self):
        states_names = ''
        if self.state:
            states_names = self.state.name
        if self.state2 is not None:
            if states_names:
                states_names += ', '
            states_names += f'{self.state2.name}'
        return states_names

    @ property
    def object_id(self) -> Optional[int]:
        if self.imported_object:
            return self.imported_object.id
        return None

    @property
    def success(self):
        return self.imported_object is not None

    def set_error(self, error):
        self.state = ProcessingState.ERROR
        self.error = error

    def set_updated(self, imported_object, fields_changes: FieldsChanges):
        self.imported_object = imported_object
        self.state = ProcessingState.UPDATED
        self.fields_before = fields_changes.values_before
        self.fields_after = fields_changes.values_after
        self.not_reset_fields = fields_changes.not_reset_fields

    def set_not_modified(self, imported_object):
        self.imported_object = imported_object
        self.state = ProcessingState.NOT_MODIFIED

    def set_not_processed(self):
        self.state = ProcessingState.NOT_PROCESSED

    def set_created(self, imported_object):
        self.imported_object = imported_object
        self.state = ProcessingState.CREATED

    def set_parent_added_to_family(self):
        self.state2 = ProcessingState.PARENT_ADDED_TO_FAMILY

    def set_bank_account_as_default(self):
        self.state2 = ProcessingState.BANK_ACCOUNT_SET_AS_DEFAULT

    def set_family_as_member(self):
        self.state2 = ProcessingState.FAMILY_SET_AS_MEMBER

    def get_fields_before_csv(self) -> str:
        return self.get_fields_csv(self.fields_before)

    def get_fields_after_csv(self) -> str:
        return self.get_fields_csv(self.fields_after)

    def get_excel_fields_csv(self) -> str:
        return self.get_fields_csv(self.excel_fields)

    def get_fields_csv(self, values):
        return ', '.join([str(f) if f is not None else '' for f in self.excel_fields])

    def get_full_state(self):
        full_state = ''
        if self.state:
            full_state = self.state.name
        if self.state2:
            full_state += f' / {self.state2.name}.'
        if self.error:
            full_state += f' {self.error}.'
        if self.state == ProcessingState.UPDATED:
            full_state += f' ({self.get_changed_fields()})'
        return full_state

    def get_changed_fields(self) -> str:
        changed_fields = ''
        for i in range(len(self.fields_before)):
            if self.fields_before[i] != self.fields_after[i] or self.field_not_reset(self.fields_after[i]):
                if changed_fields:
                    changed_fields += ', '
                if self.field_not_reset(self.fields_after[i]):
                    changed_fields += f' {self.fields_after[i]} (Reset prevented)'
                else:
                    changed_fields += f' {self.fields_before[i]} -> {self.fields_after[i]}'
        return changed_fields

    def field_not_reset(self, field):
        return field in self.not_reset_fields
