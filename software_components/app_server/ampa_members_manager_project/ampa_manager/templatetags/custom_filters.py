from typing import List

from django import template
from django.utils.safestring import mark_safe

from ampa_manager.activity.use_cases.importers.excel_column import ExcelColumn
from ampa_manager.activity.use_cases.importers.row import Row
from ampa_manager.activity.use_cases.old_importers.excel.titled_list import TitledList

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
        label = f'<span class="list_item_label">{ExcelColumn.get_column_short_label(excel_columns, column_key)}:</span>'
        value = f'<span class="list_item_value"> {raw_value}</span>'
        items.append(f'{label}{value}')
    return to_custom_list(items, '-')


@register.filter
def row_columns_formatted_values_to_html(row: Row, excel_columns: list[ExcelColumn]):
    items = []
    for column_key, column in row.columns.items():
        formatted_value = column.formatted_value if column.formatted_value else '-'
        label = f'<span class="list_item_label">{ExcelColumn.get_column_short_label(excel_columns, column_key)}:</span>'
        if column.modified:
            value = f'<span class="list_item_value_highlight"> {formatted_value}</span>'
        else:
            value = f'<span class="list_item_value"> {formatted_value}</span>'
        items.append(f'{label}{value}')
    return to_custom_list(items, '-')


@register.filter
def row_imported_models_to_html(row: Row):
    items = []
    for result in row.imported_models_results:
        if result.error:
            status_style = 'list_item_status_error'
        elif result.warning:
            status_style = 'list_item_status_warning'
        else:
            status_style = 'list_item_status_success'

        instance = str(result.instance) if result.instance else '-'
        label = f'<span class="list_item_label">{result.model_verbose_name}:</span>'
        value = f'<span class="list_item_value"> {instance}</span>'
        value += f' (<span class="{status_style}">{result.state_label}</span>)'
        items.append(f'{label}{value}')
    return to_custom_list(items, '-')


@register.filter
def row_state_to_html(row: Row):
    if row.state == Row.STATE_ERROR:
        status_style = 'row_state_error'
    elif row.state == Row.STATE_WARNING:
        status_style = 'row_state_warning'
    else:
        status_style = 'row_state_success'

    return mark_safe(f'<span class="{status_style}">{row.state_label}</span>')
