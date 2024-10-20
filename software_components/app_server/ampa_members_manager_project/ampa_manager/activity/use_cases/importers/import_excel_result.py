from ampa_manager.activity.use_cases.importers.row import Row


class ImportExcelResult:

    def __init__(self, rows: list[Row]):
        self.rows: list[Row] = rows
        self.state = None
        self.rows_with_data = 0
        self.rows_without_data = 0
        self.rows_imported_ok = 0
        self.rows_imported_warning = 0
        self.rows_not_imported = 0
        self.summarize()

    def summarize(self):
        self.calculate_rows_by_status()
        self.calculate_import_state()

    def calculate_rows_by_status(self):
        self.rows_with_data = 0
        self.rows_without_data = 0
        self.rows_imported_ok = 0
        self.rows_imported_warning = 0
        self.rows_not_imported = 0

        for row in self.rows:
            if row.is_empty:
                self.rows_without_data += 1
            else:
                self.rows_with_data += 1

            if row.state == Row.STATE_OK:
                self.rows_imported_ok += 1
            elif row.state == Row.STATE_WARNING:
                self.rows_imported_warning += 1
            elif row.state == Row.STATE_ERROR:
                self.rows_not_imported += 1

    def calculate_import_state(self):
        if self.rows_not_imported > 0:
            self.state = Row.STATE_ERROR
        elif self.rows_imported_warning > 0:
            self.state = Row.STATE_WARNING
        else:
            self.state = Row.STATE_OK
