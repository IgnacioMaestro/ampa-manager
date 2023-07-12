from typing import List

from django.urls import reverse
from django.utils.safestring import mark_safe


class Utils:

    @classmethod
    def get_model_link(cls, model_name: str, model_id: int, link_text: str, new_tab: bool = True) -> str:
        app_label = 'ampa_manager'
        model_name = model_name
        link_url = reverse('admin:%s_%s_change' % (app_label, model_name), args=[model_id])
        target = 'target="_blank"' if new_tab else ''
        return mark_safe(f'<a href="{link_url}" {target}>{link_text}</a>')

    @classmethod
    def int_list_to_csv(cls, int_list: List[int]):
        return ', '.join(str(i) for i in int_list)
