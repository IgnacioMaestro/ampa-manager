from typing import List

import xlrd
from django.core.exceptions import ValidationError

from ampa_manager.utils.excel.excel_row import ExcelRow
from ampa_manager.utils.excel.import_row_result import ImportRowResult
from ampa_manager.utils.excel.titled_list import TitledList


class ExcelImporter:

    def __init__(self, sheet_number: int, first_row_index: int, columns_to_import, file_path: str = None, file_content=None):
        self.sheet_number = sheet_number
        self.first_row_index = first_row_index
        self.columns_to_import = columns_to_import
        self.file_path = file_path
        self.file_content = file_content
        self.results: List[ImportRowResult] = []
        self.counters_before = {}
        self.counters_after = {}

        self.book, self.sheet = self.open_excel()

    def open_excel(self):
        if self.file_path:
            print(f'Loading excel file from path "{self.file_path}"')
            book = xlrd.open_workbook(filename=self.file_path)
        elif self.file_content:
            print('Loading excel file from contents')
            book = xlrd.open_workbook(file_contents=self.file_content)
        else:
            print('Unable to load excel file')
            return None, None

        sheet = book.sheet_by_index(self.sheet_number)
        print(f'Loading excel sheet "{sheet.name}"')

        return book, sheet

    def get_row_range(self, columns_indexes, row_index, formatter):
        values = []
        for column_index in columns_indexes:
            try:
                value = self.sheet.cell_value(rowx=row_index, colx=column_index)
                value = formatter(value)
            except IndexError:
                value = None
            values.append(value)
        return values

    def get_rows(self) -> List[ExcelRow]:
        rows = []
        print(f'Importing rows {self.first_row_index + 1} - {self.sheet.nrows}')
        for row_index in range(self.first_row_index, self.sheet.nrows):
            rows.append(self.get_row(row_index))
        return rows

    def get_row(self, row_index: int) -> ExcelRow:
        row = ExcelRow(row_index)

        for column_settings in self.columns_to_import:
            col_index = column_settings[0]
            formatter = column_settings[1]
            key = column_settings[2]
            value = self.get_cell_value(row_index, col_index)
            try:
                row.values[key] = formatter(value)
            except ValidationError as e:
                row.values[key] = None
                row.error = f'Error formatting column: {key} = {value}: {str(e)}'
                break

        return row

    def get_cell_value(self, row_index, col_index):
        return self.sheet.cell_value(rowx=row_index, colx=col_index)

    def add_result(self, result: ImportRowResult):
        self.results.append(result)

    @property
    def total_rows(self) -> int:
        return self.sheet.nrows - self.first_row_index

    @property
    def successfully_imported_rows(self) -> int:
        success = 0
        for result in self.results:
            if result.success:
                success += 1
        return success

    def get_logs(self) -> List[str]:
        logs = []
        for result in self.results:
            logs.append(str(result))
        return logs

    def get_results(self) -> TitledList:
        logs = TitledList('Results')
        for result in self.results:
            logs.append_sublist(result.as_titled_list())
        return logs

    def get_summary(self) -> TitledList:
        summary = TitledList('Summary')

        totals_by_model, totals_by_status, errors, warnings, created_families, success_count, not_success_count = \
            ImportRowResult.get_totals(self.results)

        summary_totals = TitledList('Total')
        summary_totals.append_element(f'Rows imported successfully: {success_count}/{len(self.results)}')
        summary_totals.append_element(f'Rows not imported: {not_success_count}/{len(self.results)}')
        summary.append_sublist(summary_totals)

        summary_errors = TitledList(f'Errors: {len(errors)}')
        for row_index, error in errors.items():
            summary_errors.append_element(f'Row {row_index+1}: {error}')
        summary.append_sublist(summary_errors)

        summary_warnings = TitledList('Warnings')
        if len(created_families) > 0:
            summary_created_families = TitledList(f'{len(created_families)} families were created')
            for row_index, family in created_families.items():
                created_family_element = TitledList(family.get_html_link())
                for similar_family in family.get_similar_names_families():
                    created_family_element.append_element(similar_family.get_html_link())
                summary_created_families.append_sublist(created_family_element)
            summary_warnings.append_sublist(summary_created_families)

        for row_index, warning in warnings.items():
            summary_warnings.append_element(f'- Row {row_index + 1}: {warning}')
        summary.append_sublist(summary_warnings)

        summary_by_model = TitledList('Results by model')
        for model_name, model_totals in totals_by_model.items():
            variation = ImportRowResult.get_variation(self.counters_before[model_name], self.counters_after[model_name])

            summary_model = TitledList(f'{model_name}: {variation}')
            for state, state_count in model_totals.items():
                summary_model.append_element(f'{state.name}: {state_count}')
            summary_by_model.append_sublist(summary_model)
        summary.append_sublist(summary_by_model)

        summary_by_status = TitledList('Results by status')
        for state, state_totals in totals_by_status.items():
            summary_state = TitledList(str(state.name))
            for model_name, model_count in state_totals.items():
                summary_state.append_element(f'{model_name}: {model_count}')
            summary_by_status.append_sublist(summary_state)
        summary.append_sublist(summary_by_status)

        return summary
