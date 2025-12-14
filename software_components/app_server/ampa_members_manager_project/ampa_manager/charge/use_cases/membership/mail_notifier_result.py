from typing import Optional


class MailNotifierResult:
    def __init__(self, success_emails: list[str] = None, error_emails: list[str] = None, error: Optional[str] = None):
        self.success_emails = success_emails if success_emails else []
        self.error_emails = error_emails if error_emails else []
        self.error = error

    def append_success_emails(self, emails: list[str]):
        if emails:
            self.success_emails.extend(emails)

    def append_error_emails(self, emails: list[str]):
        if emails:
            self.error_emails.extend(emails)

    def get_as_html(self):
        html = '<ul>'
        html += f'<li>Sent emails: {len(self.success_emails)}</li>'
        html += f'<li>Error emails: {len(self.error_emails)}</li>'
        html += f'<li>Error: {self.error}</li>'
        if len(self.error_emails) > 0:
            html += f'<li><ul>'
            for email in self.error_emails:
                html += f'<li>{email}</li>'
            html += '</ul></li>'
        html = '</ul>'
        return html
