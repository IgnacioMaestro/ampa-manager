from django.urls import reverse
from django.utils.safestring import mark_safe


class Utils:

    @classmethod
    def get_model_link(cls, model_name: str, model_id: int, link_text) -> str:
        app_label = 'ampa_manager'
        model_name = model_name
        link_url = reverse('admin:%s_%s_change' % (app_label, model_name), args=[model_id])
        return mark_safe(f'<a href="{link_url}">{link_text}</a>')
