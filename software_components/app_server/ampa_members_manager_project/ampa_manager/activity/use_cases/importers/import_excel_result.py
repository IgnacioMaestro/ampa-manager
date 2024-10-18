from ampa_manager.activity.use_cases.importers.row import Row


class ImportExcelResult:

    def __init__(self, rows: list[Row]):
        self.rows: list[Row] = rows
        self.state = None
        self.rows_detected = 100
        self.rows_imported_ok = 1
        self.rows_imported_warning = 2
        self.rows_not_imported = 3

        self.summarize()

    def summarize(self):
        for row in self.rows:
            self.rows_detected += 1
            if row.state == Row.STATE_OK:
                self.rows_imported_ok += 1
            elif row.state == Row.STATE_WARNING:
                self.rows_imported_warning += 1
            elif row.state == Row.STATE_ERROR:
                self.rows_not_imported += 1

        if self.rows_not_imported > 0:
            self.state = Row.STATE_ERROR
        elif self.rows_imported_warning > 0:
            self.state = Row.STATE_WARNING
        else:
            self.state = Row.STATE_OK
