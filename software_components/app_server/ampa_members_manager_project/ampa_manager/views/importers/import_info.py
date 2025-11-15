from dataclasses import dataclass

from ampa_manager.activity.use_cases.old_importers.excel.titled_list import TitledList


@dataclass
class ImportInfo:
    total_rows: int
    success_rows: int
    summary: TitledList
    results: TitledList

    def success(self) -> bool:
        return self.total_rows > 0 and self.total_rows == self.success_rows
