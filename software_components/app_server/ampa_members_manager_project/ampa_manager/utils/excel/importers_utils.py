from ampa_manager.utils.string_utils import StringUtils


def get_excel_columns(columns_to_import):
    columns = []
    for column in columns_to_import:
        index = column[0]
        letter = StringUtils.get_excel_column_letter(index).upper()
        label = column[3]
        columns.append([letter, label])
    return columns
