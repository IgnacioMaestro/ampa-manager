from typing import Optional


class MailNotifierResult:
    def __init__(self, success_emails: list[str], error_emails: list[str] = None, error: Optional[str] = None):
        self.success_emails = success_emails
        self.error_emails = error_emails
        self.error = error
