from django import template

from ampa_manager.utils.excel.titled_list import TitledList

register = template.Library()


@register.filter
def titled_list_to_ul(titled_list: TitledList):
    html = '<ul>'
    html += f'<li>{titled_list.title}</li>'

    if titled_list.elements:
        for element in titled_list.elements:
            html += f'<li>{element}</li>'

    if titled_list.sublists:
        for sublist in titled_list.sublists:
            html += '<li>'
            html += titled_list_to_ul(sublist)
            html += '</li>'

    html += '</ul>'

    return html
