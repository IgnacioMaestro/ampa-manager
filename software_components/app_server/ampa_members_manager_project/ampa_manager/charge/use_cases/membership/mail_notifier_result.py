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
