from ampa_manager.management.commands.results.processing_state import ProcessingState


class ImportResult:
    def __init__(self, state=ProcessingState.NOT_PROCESSED, state2=None, error=None):
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
