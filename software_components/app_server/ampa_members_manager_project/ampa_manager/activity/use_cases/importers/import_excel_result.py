from ampa_manager.activity.use_cases.importers.row import Row


class ImportExcelResult:

    def __init__(self, rows: list[Row]):
        self.rows: list[Row] = rows
        self.state = None
        self.rows_detected = 100
        self.rows_ok = 0
        self.rows_warning = 0
        self.rows_error = 0
