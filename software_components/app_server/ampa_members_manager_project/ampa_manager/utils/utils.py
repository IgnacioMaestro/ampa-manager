from typing import List

from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy


class Utils:

    @classmethod
    def get_model_instance_link(cls, model_name: str, model_id: int, link_text: str, new_tab: bool = True) -> str:
        app_label = 'ampa_manager'
        link_url = reverse('admin:%s_%s_change' % (app_label, model_name), args=[model_id])
        target = 'target="_blank"' if new_tab else ''
        return mark_safe(f'<a href="{link_url}" {target}>{link_text}</a>')

    @classmethod
    def get_model_link(cls, model_name: str, link_text: str, new_tab: bool = True, filters: str = None) -> str:
        app_label = 'ampa_manager'
        link_url = reverse('admin:%s_%s_changelist' % (app_label, model_name))
        if filters:
            link_url += f'?{filters}'
        target = 'target="_blank"' if new_tab else ''
        return mark_safe(f'<a href="{link_url}" {target}>{link_text}</a>')

    @classmethod
    def int_list_to_csv(cls, int_list: List[int]):
        return ', '.join(str(i) for i in int_list)

    @classmethod
    def create_bic_error_message(cls) -> str:
        link = Utils.get_model_link(
            model_name='bankaccount', link_text=gettext_lazy("Review the Bank Accounts without BIC"),
            filters='bic=without')
        return mark_safe(gettext_lazy("BIC error") + " " + link)
