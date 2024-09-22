from ampa_manager.activity.use_cases.importers.row import Row


class ImportResult:

    def __init__(self, rows: list[Row]):
        self.rows: list[Row] = rows
        self.results: list = []

    @property
    def success(self) -> bool:
        return True
