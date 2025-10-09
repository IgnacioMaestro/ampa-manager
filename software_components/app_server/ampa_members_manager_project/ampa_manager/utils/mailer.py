from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class Mailer:

    @classmethod
    def send_template_mail(cls, subject: str, body_html_template: str, body_html_context: dict,
                           to_recipients: list[str] = None, bcc_recipients: list[str] = None,
                           reply_to: str = None, body_text_content: str = None):
        body_html_context.update(cls.__get_base_email_context())

        if to_recipients is None:
            to_recipients = []

        if bcc_recipients is None:
            bcc_recipients = []

        if reply_to is not None:
            reply_to = [settings.DEFAULT_FROM_EMAIL]

        html_content = render_to_string(body_html_template, body_html_context)
        msg = EmailMultiAlternatives(
            subject, body=body_text_content, from_email=settings.DEFAULT_FROM_EMAIL, to=to_recipients,
            bcc=bcc_recipients, reply_to=reply_to)
        msg.attach_alternative(html_content, "text/html")
        try:
            msg.send()
        except Exception as e:
            return str(e)
        return None

    @classmethod
    def __get_base_email_context(cls) -> dict:
        return {
            'logo_url': settings.LOGO_FULL_URL
        }
