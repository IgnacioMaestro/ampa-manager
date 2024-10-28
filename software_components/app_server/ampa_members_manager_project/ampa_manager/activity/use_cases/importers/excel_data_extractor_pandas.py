import math

import pandas as pd
from io import BytesIO

from ampa_manager.activity.use_cases.importers.column import Column
from ampa_manager.activity.use_cases.importers.row import Row


class ExcelDataExtractorPandas:
    def __init__(self, excel_content, sheet_number: int, first_row_index: int, columns_to_extract: list):
        self.excel_content = excel_content
        self.sheet_number = sheet_number
        self.first_row_index = first_row_index
        self.columns_to_extract = columns_to_extract

        self.df = pd.read_excel(BytesIO(self.excel_content), sheet_name=self.sheet_number)

        if self.first_row_index > len(self.df):
            raise Exception('Invalid first row index')

    def extract(self) -> list[Row]:
        rows = []
        for row_index in range(self.first_row_index, len(self.df)):
            row = Row(row_index)

            for excel_column in self.columns_to_extract:
                row.add_value(
                    excel_column.key, self.get_column(row_index, excel_column.index, excel_column.formatter))

            rows.append(row)
        return rows

    def get_column(self, row_index: int, col_index: int, formatter) -> Column:
        raw_value = None
        formatted_value = None
        error = None

        try:
            raw_value = self.df.iat[row_index, col_index]

            if isinstance(raw_value, float) and math.isnan(raw_value):
                raw_value = None

            formatted_value = formatter(raw_value) if raw_value is not None else None
        except IndexError:
            raw_value = None
            formatted_value = None
        except Exception as e:
            if hasattr(e, 'message'):
                error = e.message
            else:
                error = str(e)

        return Column(raw_value, formatted_value, error)
