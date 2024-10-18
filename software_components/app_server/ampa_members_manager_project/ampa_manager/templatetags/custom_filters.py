from typing import List

from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.activity.use_cases.importers.excel_column import ExcelColumn
from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.activity.use_cases.importers.row import Row
from ampa_manager.activity.use_cases.old_importers.excel.titled_list import TitledList
from ampa_manager.family.models.child import Child

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
    return to_custom_list(items, '·')


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
    return to_custom_list(items, '·')


def get_instance_details(result: ImportModelResult) -> str:
    if result.instance:
        if result.model == CustodyRegistration:
            return f'{result.instance.holder}, {result.instance.assisted_days} ' + _('assisted days')
        elif result.model == CampsRegistration:
            return f'{result.instance.holder}'
        elif result.model == AfterSchoolRegistration:
            return f'{result.instance.holder}'
        elif result.model == Child:
            return f'{result.instance.name} {str(result.instance.family.surnames)}, {result.instance.level}'
        else:
            return str(result.instance)
    else:
        return '-'


@register.filter
def row_imported_models_to_html(row: Row):
    items = []
    for result in row.imported_models_results:
        label = f'<span class="list_item_label">{result.model_verbose_name}:</span>'
        value = f'<span class="list_item_value"> {get_instance_details(result)}</span>'
        value += f' <span class="imported_model_status_{result.state.lower()}">{result.state_label}</span>'
        if result.error_message:
            value += f'<br/>&nbsp;&nbsp; - <span class="imported_model_error">({result.error_message})</span>'
        for warning_message in result.warnings:
            value += f'<br/>&nbsp;&nbsp; - <span class="imported_model_warning">({warning_message})</span>'
        if result.state != ImportModelResult.NOT_MODIFIED:
            for warning_message in result.minor_warnings:
                value += f'<br/>&nbsp;&nbsp; - <span class="imported_model_warning">({warning_message})</span>'
        items.append(f'{label}{value}')
    return to_custom_list(items, '·')


@register.filter
def row_state_to_html(row: Row):
    if row.state == Row.STATE_ERROR:
        status_style = 'row_state_error'
    elif row.state == Row.STATE_WARNING:
        status_style = 'row_state_warning'
    else:
        status_style = 'row_state_success'

    return mark_safe(f'<span class="{status_style}">{row.state_label}</span>')
