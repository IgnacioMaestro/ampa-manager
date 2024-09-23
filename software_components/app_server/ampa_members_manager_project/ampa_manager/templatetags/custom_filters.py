from typing import List

from django import template
from django.utils.safestring import mark_safe

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
