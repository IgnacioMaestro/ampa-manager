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
    new_line_tab_hyphen = '<br/>&nbsp;&nbsp; - '

    for column_key, column in row.columns.items():
        formatted_value = column.formatted_value if column.formatted_value else '-'
        label = generate_span('list_item_label', ExcelColumn.get_column_short_label(excel_columns, column_key))

        if column.error:
            value = generate_span('formatted_column_value_error', formatted_value)
            value += new_line_tab_hyphen + generate_span('formatted_column_value_error', column.error)
        elif column.modified:
            value = generate_span('formatted_column_value_warning', formatted_value)
        else:
            value = generate_span('formatted_column_value', formatted_value)
        items.append(f'{label} {value}')
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
    new_line_tab_hyphen = '<br/>&nbsp;&nbsp; - '

    for result in row.imported_models_results:
        result_details = ''
        result_details += generate_span('list_item_label', result.model_verbose_name)
        result_details += ' ' + generate_span('list_item_value', get_instance_details(result))
        result_details += ' ' + generate_span(f'imported_model_status_{result.state.lower()}', result.state_label)

        # CHANGED FIELDS
        if result.state == ImportModelResult.UPDATED:
            for i in range(len(result.values_before)):
                value_before = result.values_before[i]
                value_after = result.values_after[i]
                if value_before != value_after:
                    result_details += new_line_tab_hyphen + generate_span('imported_model_changed_field', f'{value_before} -> {value_after}')

        # ERROR
        if result.error_message:
            result_details += new_line_tab_hyphen + generate_span('imported_model_error', result.error_message)

        # WARNINGS
        for warning_message in result.warnings:
            result_details += new_line_tab_hyphen + generate_span('imported_model_warning', warning_message)

        # MINOR WARNINGS
        if result.state != ImportModelResult.NOT_MODIFIED:
            for warning_message in result.minor_warnings:
                result_details += new_line_tab_hyphen + generate_span('imported_model_warning', warning_message)

        if result.instance:
            result_details = Utils.get_model_instance_link(result.model.__name__.lower(), result.instance.id, result_details)

        items.append(result_details)

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

    return mark_safe(generate_span(status_style, row.state_label))


@register.filter
def import_state_to_html(state: str):
    if state == Row.STATE_ERROR:
        status_style = 'row_state_error'
    elif state == Row.STATE_WARNING:
        status_style = 'row_state_warning'
    else:
        status_style = 'row_state_ok'

    return mark_safe(generate_span(status_style, state.upper()))
