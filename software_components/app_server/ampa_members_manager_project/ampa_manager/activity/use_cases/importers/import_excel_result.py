from ampa_manager.activity.use_cases.importers.row import Row


class ImportExcelResult:

    def __init__(self, rows: list[Row]):
        self.rows: list[Row] = rows

    @property
    def success(self) -> bool:
        return True
