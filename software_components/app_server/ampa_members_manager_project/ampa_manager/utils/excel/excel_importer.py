from typing import List

import pandas as pd
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from pandas import DataFrame, Series

from ampa_manager.utils.excel.excel_row import ExcelRow
from ampa_manager.utils.excel.import_row_result import ImportRowResult
from ampa_manager.utils.excel.titled_list import TitledList


class ExcelImporter:

    def __init__(self, sheet_number: int, first_row_index: int, columns_to_import, file_content):
        self.sheet_number = sheet_number
        self.first_row_index = first_row_index
        self.columns_to_import = columns_to_import
        self.file_content = file_content
        self.data: DataFrame = pd.read_excel(file_content, sheet_name=0, header=None)
        self.results: List[ImportRowResult] = []
        self.counters_before = {}
        self.counters_after = {}

    def get_rows(self) -> List[ExcelRow]:
        rows = []

        print(self.data.head())
        for row_index, row_series in self.data.iterrows():
            print(f'index {row_index}: {row_series[0]}')

        for row_index, row_series in self.data.iterrows():
            if row_index < self.first_row_index:
                continue
            row = self.get_row(int(row_index), row_series)
            if not self.is_empty(row):
                rows.append(row)
        return rows

    def is_empty(self, row: ExcelRow) -> bool:
        for value in row.values.values():
            if value not in [None, '', '0', 0]:
                return False
        return True

    def get_row(self, row_index: int, row: Series) -> ExcelRow:
        excel_row = ExcelRow(row_index)

        for column_settings in self.columns_to_import:
            col_index = column_settings[0]
            formatter = column_settings[1]
            key = column_settings[2]

            value = row[col_index]
            if pd.isna(value):
                value = None

            try:
                excel_row.values[key] = formatter(value)
            except ValidationError as e:
                excel_row.values[key] = None
                excel_row.error = f'Error formatting column: {key} = {value}: {str(e)}'
                break

        return excel_row

    def add_result(self, result: ImportRowResult):
        self.results.append(result)

    @property
    def total_rows(self) -> int:
        return len(self.data) - self.first_row_index

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
        summary = TitledList(_('Summary'))

        totals_by_model, totals_by_status, errors, warnings, created_families, success_count, not_success_count = \
            ImportRowResult.get_totals(self.results)

        summary_totals = TitledList(_('Total'))
        summary_totals.append_element(_('Rows imported successfully') + ': ' + f'{success_count}/{len(self.results)}')
        summary_totals.append_element(_('Rows not imported') + ': ' + f'{not_success_count}/{len(self.results)}')
        summary.append_sublist(summary_totals)

        summary_errors = TitledList(_('Errors') + ': ' + str(len(errors)))
        for row_index, error in errors.items():
            summary_errors.append_element(_('Row') + f' {row_index+1}: {error}')
        summary.append_sublist(summary_errors)

        summary_warnings = TitledList(_('Warnings'))
        if len(created_families) > 0:
            summary_created_families = TitledList(_("%(created_families)s families created") % {'created_families': len(created_families)})

            for row_index, family in created_families.items():
                created_family_element = TitledList(family.get_html_link())
                for similar_family in family.get_similar_names_families():
                    created_family_element.append_element(similar_family.get_html_link())
                summary_created_families.append_sublist(created_family_element)
            summary_warnings.append_sublist(summary_created_families)

        for row_index, warning in warnings.items():
            summary_warnings.append_element(f'- Row {row_index + 1}: {warning}')
        summary.append_sublist(summary_warnings)

        summary_by_model = TitledList(_('Results by model'))
        for model_name, model_totals in totals_by_model.items():
            variation = ImportRowResult.get_variation(self.counters_before[model_name], self.counters_after[model_name])

            summary_model = TitledList(f'{model_name}: {variation}')
            for state, state_count in model_totals.items():
                summary_model.append_element(f'{state.name}: {state_count}')
            summary_by_model.append_sublist(summary_model)
        summary.append_sublist(summary_by_model)

        summary_by_status = TitledList(_('Results by status'))
        for state, state_totals in totals_by_status.items():
            summary_state = TitledList(str(state.name))
            for model_name, model_count in state_totals.items():
                summary_state.append_element(f'{model_name}: {model_count}')
            summary_by_status.append_sublist(summary_state)
        summary.append_sublist(summary_by_status)

        return summary
