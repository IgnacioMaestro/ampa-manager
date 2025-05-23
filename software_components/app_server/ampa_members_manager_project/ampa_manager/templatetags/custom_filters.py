from typing import List

from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.use_cases.importers.excel_column import ExcelColumn
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.activity.use_cases.importers.row import Row
from ampa_manager.activity.use_cases.importers.titled_list import TitledList
from ampa_manager.templatetags.html_blocks import html_new_line_tab, html_new_line_tab_hyphen, html_space
from ampa_manager.utils.utils import Utils

register = template.Library()


@register.filter
def list_to_csv(values: List):
    return ','.join(values)


@register.filter
def titled_list_to_ul(titled_list: TitledList):
    return generate_html_list_from_title_list(titled_list, numbered=False)


@register.filter
def titled_list_to_ol(titled_list: TitledList):
    return generate_html_list_from_title_list(titled_list, numbered=True)


def generate_html_list_from_title_list(titled_list: TitledList, level=1, numbered=False, collapsable=True):
    if titled_list is None or titled_list == '':
        return ''

    if titled_list.title:
        onclick = ''
        if collapsable:
            onclick = f'showHideSection(\'{titled_list.id}\')'
        html = f'<h{level} onclick="{onclick}">{titled_list.title}</h{level}>'
    else:
        html = ''

    list_tag = 'ol' if numbered else 'ul'

    html += f'<{list_tag} id="{titled_list.id}">'

    if titled_list.elements:
        for element in titled_list.elements:
            html += f'<li>{element}</li>'

    if titled_list.sublists:
        for sublist in titled_list.sublists:
            html += '<li>'
            html += generate_html_list_from_title_list(sublist, level=level+1, numbered=numbered, collapsable=False)
            html += '</li>'

    html += f'</{list_tag}>'

    return mark_safe(html)

@register.filter
def excel_column_to_html(column: ExcelColumn):
    text = f'{_("Column")} {column.letter}: {column.label}'
    span_html = generate_span(column.style, text)
    return mark_safe(f'<li>{span_html}</li>')

@register.filter
def to_unordered_list(items: list[str]):
    if not isinstance(items, list):
        return ''

    list_items = ''.join(f'<li>{item}</li>' for item in items)
    return mark_safe(f'<ul>{list_items}</ul>')


@register.filter
def to_custom_list(items: list[str], symbol: str):
    if not isinstance(items, list):
        return ''

    custom_list = ''
    for item in items:
        custom_list += f'{symbol} {item}<br/>'

    return mark_safe(custom_list)


@register.filter
def row_columns_raw_values_to_html(row: Row, excel_columns: list[ExcelColumn]):
    items = []
    for column_key, column in row.columns.items():
        raw_value = column.raw_value if column.raw_value else '-'
        label = generate_span('list_item_label', ExcelColumn.get_column_short_label(excel_columns, column_key))
        value = generate_span('list_item_value', raw_value)
        items.append(f'{label} {value}')
    return to_custom_list(items, '·')


@register.filter
def row_columns_formatted_values_to_html(row: Row, excel_columns: list[ExcelColumn]):
    items = []

    for column_key, column in row.columns.items():
        formatted_value = column.formatted_value if column.formatted_value else '-'
        label = generate_span('list_item_label', ExcelColumn.get_column_short_label(excel_columns, column_key))

        if column.error:
            value = generate_span('formatted_column_value_error', formatted_value)
            value += html_new_line_tab + generate_span('formatted_column_value_error', column.error)
        elif column.modified:
            value = generate_span('formatted_column_value_warning', formatted_value)
        else:
            value = generate_span('formatted_column_value', formatted_value)
        items.append(f'{label} {value}')
    return to_custom_list(items, '·')


@register.filter
def row_imported_models_to_html(row: Row):
    items = []

    for result in row.imported_models_results:
        result_details = ''
        result_details += generate_span('list_item_label', result.model_verbose_name)
        result_details += ' ' + generate_span('list_item_value', result.instance_str)
        if result.state not in [ImportModelResult.OMITTED, ImportModelResult.ERROR]:
            result_details += ' ' + generate_span(f'imported_model_status_{result.state.lower()}', result.state_label)

        # CHANGED FIELDS
        if result.state == ImportModelResult.UPDATED:
            for modified_field in result.modified_fields:
                value_before = '-' if modified_field.value_before is None else modified_field.value_before
                value_after = '-' if modified_field.value_after is None else modified_field.value_after
                result_details += (html_new_line_tab_hyphen +
                                   generate_span('list_item_label',
                                                 f'{modified_field.field_name}') + ' ' +
                                   generate_span('imported_model_changed_field', f'{value_before} → {value_after}'))

        # ERROR
        if result.error_message:
            result_details += html_new_line_tab + generate_span('imported_model_error', result.error_message)

        # WARNINGS
        for warning_message in result.warnings:
            result_details += html_new_line_tab + generate_span('imported_model_warning', warning_message)

        # MINOR WARNINGS
        if result.state != ImportModelResult.NOT_MODIFIED:
            for warning_message in result.minor_warnings:
                result_details += html_new_line_tab + generate_span('imported_model_warning', warning_message)

        if result.instance:
            result_details = Utils.get_model_instance_link(result.model.__name__.lower(), result.instance.id, result_details)

        items.append(result_details)

    if row.error:
        items.append(generate_span('imported_model_error', row.error))

    return to_custom_list(items, '·')


def generate_span(class_name: str, content: str) -> str:
    return f'<span class="{class_name}">{content}</span>'


@register.filter
def row_state_to_html(row: Row):
    if row.state == Row.STATE_ERROR:
        status_style = 'row_state_error'
    elif row.state == Row.STATE_WARNING:
        status_style = 'row_state_warning'
    elif row.state == Row.STATE_OMITTED:
        status_style = 'row_state_omitted'
    else:
        status_style = 'row_state_ok'

    return mark_safe(generate_span(status_style, complete_with_spaces(row.state_label, 14)))


def complete_with_spaces(string: str, length: int) -> str:
    spaces = length - len(string)
    if spaces > 0:
        return str(html_space * int(spaces / 2)) + string + str(html_space * int(spaces / 2))
    return string


@register.filter
def import_state_to_html(state: str):
    if state == Row.STATE_ERROR:
        status_style = 'row_state_error'
    elif state == Row.STATE_WARNING:
        status_style = 'row_state_warning'
    else:
        status_style = 'row_state_ok'

    return mark_safe(generate_span(status_style, state.upper()))
