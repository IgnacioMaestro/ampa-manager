from ampa_manager.management.commands.results.processing_state import ProcessingState


class ModelImportResult:
    def __init__(self, class_name, state=ProcessingState.NOT_PROCESSED, state2=None, error=None):
        self.class_name = class_name
        self.imported_object = None
        self.state = state
        self.state2 = state2
        self.error = error
        self.fields_before = []
        self.fields_after = []

    @property
    def success(self):
        return self.imported_object is not None

    def set_error(self, error):
        self.state = ProcessingState.ERROR
        self.error = error

    def set_updated(self, imported_object, fields_before, fields_after):
        self.imported_object = imported_object
        self.state = ProcessingState.UPDATED
        self.fields_before = fields_before
        self.fields_after = fields_after

    def set_not_modified(self, imported_object):
        self.imported_object = imported_object
        self.state = ProcessingState.NOT_MODIFIED

    def set_not_processed(self):
        self.state = ProcessingState.NOT_PROCESSED

    def set_created(self, imported_object):
        self.imported_object = imported_object
        self.state = ProcessingState.CREATED

    def set_added_to_family(self):
        self.state2 = ProcessingState.PARENT_ADDED_TO_FAMILY

    def set_as_default(self):
        self.state2 = ProcessingState.BANK_ACCOUNT_SET_AS_DEFAULT

    def get_fields_before_csv(self):
        return ', '.join(self.fields_before)

    def get_fields_after_csv(self):
        return ', '.join(self.fields_after)

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

    def get_changed_fields(self):
        changed_fields = ''
        for i in range(len(self.fields_before)):
            if self.fields_before[i] != self.fields_after[i]:
                if changed_fields:
                    changed_fields += ', '
                changed_fields += f' {self.fields_before[i]} -> {self.fields_after[i]}'
        return changed_fields
