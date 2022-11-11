from ampa_members_manager.management.commands.import_command.processing_state import ProcessingState


class ProcessingResult:
    def __init__(self, class_name, row_index, state=ProcessingState.NOT_PROCESSED, state2=None, error=None):
        self.class_name = class_name
        self.row_index = row_index
        self.state = state
        self.state2 = state2
        self.error = error
        self.fields = []
    
    def set_state(self, state):
        self.state = state
    
    def set_state2(self, state2):
        self.state2 = state2

    def set_error(self, error):
        self.state = ProcessingState.ERROR
        self.error = error
    
    def set_updated(self):
        self.state = ProcessingState.UPDATED

    def set_not_modified(self):
        self.state = ProcessingState.NOT_MODIFIED
    
    def set_not_processed(self):
        self.state = ProcessingState.NOT_PROCESSED
    
    def set_created(self):
        self.state = ProcessingState.CREATED
    
    def set_added_to_family(self):
        self.state2 = ProcessingState.UPDATED_ADDED_TO_FAMILY
    
    def set_as_default(self):
        self.state2 = ProcessingState.UPDATED_AS_DEFAULT
