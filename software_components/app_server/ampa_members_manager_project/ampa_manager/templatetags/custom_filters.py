from django import template
from django.utils.safestring import mark_safe

from ampa_manager.utils.excel.titled_list import TitledList

register = template.Library()


@register.filter
def titled_list_to_ul(titled_list: TitledList, level=1):
    if titled_list.title:
        html = f'<h{level}>{titled_list.title}</h{level}>'
    else:
        html = ''

    html += '<ul>'

    if titled_list.elements:
        for element in titled_list.elements:
            html += f'<li>{element}</li>'

    if titled_list.sublists:
        for sublist in titled_list.sublists:
            html += '<li>'
            html += titled_list_to_ul(sublist, level=level+1)
            html += '</li>'

    html += '</ul>'

    return mark_safe(html)
