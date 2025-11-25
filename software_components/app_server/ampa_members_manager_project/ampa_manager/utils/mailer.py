from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from ampa_manager.charge.use_cases.membership.mail_notifier_result import MailNotifierResult


class Mailer:
    MAX_ADDRESSES_IN_A_SINGLE_MAIL = 99

    @classmethod
    def send_template_mail(cls, subject: str, body_html_template: str, body_html_context: dict,
                           bcc_recipients: list[str] = None, reply_to: str = None,
                           body_text_content: str = None) -> MailNotifierResult:
        result: MailNotifierResult = MailNotifierResult()

        if not cls.settings_are_ok():
            result.error_emails = bcc_recipients
            result.error = 'Email settings not configured'
        elif bcc_recipients is None:
            result.error = 'No recipients specified'
        else:
            if reply_to is None:
                reply_to = [settings.DEFAULT_REPLY_TO_EMAIL]
            html_content = cls.__get_html_content(body_html_template, body_html_context)

            for batch_emails in cls.__group_recipients_in_batches(bcc_recipients):
                msg = EmailMultiAlternatives(
                    subject, body=body_text_content, from_email=settings.DEFAULT_FROM_EMAIL, to=[],
                    bcc=batch_emails, reply_to=reply_to)
                msg.attach_alternative(html_content, "text/html")
                try:
                    msg.send()
                    result.append_success_emails(batch_emails)
                except Exception as e:
                    result.append_error_emails(batch_emails)
                    result.error = str(e)
                    break
        return result

    @classmethod
    def __get_html_content(cls, body_html_template: str, body_html_context) -> str:
        body_html_context.update(cls.__get_base_email_context())
        return render_to_string(body_html_template, body_html_context)

    @classmethod
    def settings_are_ok(cls) -> bool:
        return settings.EMAIL_HOST and settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD

    @classmethod
    def __get_base_email_context(cls) -> dict:
        return {
            'logo_url': settings.LOGO_FULL_URL
        }

    @classmethod
    def __group_recipients_in_batches(cls, recipients: list[str]) -> list[list[str]]:
        if len(recipients) < cls.MAX_ADDRESSES_IN_A_SINGLE_MAIL:
            return [recipients]
        else:
            batches = []
            step = cls.MAX_ADDRESSES_IN_A_SINGLE_MAIL
            for i in range(0, len(recipients), step):
                batches.append(recipients[i:i + step])
            return batches
