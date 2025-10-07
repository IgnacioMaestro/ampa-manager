from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class Mailer:

    @classmethod
    def send_template_mail(cls, recipients: list[str], subject: str, body_html_template: str, body_html_context: dict,
                           body_text_content):
        body_html_context['logo_url'] = settings.LOGO_FULL_URL

        html_content = render_to_string(body_html_template, body_html_context)
        msg = EmailMultiAlternatives(subject, body_text_content, settings.DEFAULT_FROM_EMAIL, recipients)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
