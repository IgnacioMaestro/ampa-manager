from ampa_manager.management.commands.results.processing_state import ProcessingState


class ImportMemberResult:
    def __init__(self, class_name, row_index, state=ProcessingState.NOT_PROCESSED, state2=None, error=None, message=None):
        self.class_name = class_name
        self.row_index = row_index
        self.state = state
        self.state2 = state2
        self.error = error
        self.message = message
        self.fields_excel = []
        self.fields_before = []
        self.fields_after = []

    def set_error(self, error):
        self.state = ProcessingState.ERROR
        self.error = error
    
    def set_updated(self, fields_before, fields_after, message=None):
        self.state = ProcessingState.UPDATED
        self.fields_before = fields_before
        self.fields_after = fields_after
        self.message = message

    def set_not_modified(self, message=None):
        self.state = ProcessingState.NOT_MODIFIED
        self.message = message
    
    def set_not_processed(self, message=None):
        self.state = ProcessingState.NOT_PROCESSED
        self.message = message
    
    def set_created(self, message=None):
        self.state = ProcessingState.CREATED
        self.message = message
    
    def set_added_to_family(self, message=None):
        self.state2 = ProcessingState.ADDED_TO_FAMILY
        self.message = message
    
    def set_as_default(self, message=None):
        self.state2 = ProcessingState.SET_AS_DEFAULT
        self.message = message
    
    def get_full_state(self):
        full_state = ''
        if self.state:
            full_state = self.state.name
        if self.state2:
            full_state += f' / {self.state2.name}.'
        if self.message:
            full_state += f' {self.message}.'
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
    
    def get_fields_before_csv(self):
        return ImportMemberResult.get_fields_csv(self.fields_before)
    
    def get_fields_after_csv(self):
        return ImportMemberResult.get_fields_csv(self.fields_after)
    
    def get_fields_excel_csv(self):
        return ImportMemberResult.get_fields_csv(self.fields_excel)
    
    @staticmethod
    def get_fields_csv(fields):
        fields_csv = ''
        for field in fields:
            if fields_csv == '':
                fields_csv += f'{field}'
            else:
                fields_csv += f', {field}'
        return fields_csv
