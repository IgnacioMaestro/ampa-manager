from typing import Optional

from django.conf import settings
from django.utils.formats import date_format

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ampa_manager.charge.models.fee.fee import Fee
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.charge.use_cases.membership.mail_notifier_result import MailNotifierResult
from ampa_manager.utils.mailer import Mailer


class AfterSchoolRemittanceNotifier:
    MAIL_SUBJECT = 'Cuota de extraescolares | Eskolaz kanpoko kuota'
    MAIL_TEMPLATE = 'emails/after_school_remittance_email.html'
    TYPE_ENROLLMENT = 'ENROLLMENT'
    TYPE_FIRST_FEE = 'FIRST_FEE'
    TYPE_LAST_FEE = 'LAST_FEE'

    def __init__(self, remittance: AfterSchoolRemittance, notify_type: int):
        self.notify_type: int = notify_type
        self.remittance: AfterSchoolRemittance = remittance
        self.course: AcademicCourse = ActiveCourse.load()
        self.pay_date: str = self.__get_formatted_pay_date()

    def test_notify(self) -> MailNotifierResult:
        partial_results = []
        emails = [settings.TEST_EMAIL_RECIPIENT]
        for notify_type in [self.TYPE_ENROLLMENT, self.TYPE_FIRST_FEE, self.TYPE_LAST_FEE]:
            partial_result: MailNotifierResult = Mailer.send_template_mail(
                bcc_recipients=emails,
                subject=self.MAIL_SUBJECT,
                body_html_template=self.MAIL_TEMPLATE,
                body_html_context=self.__get_test_template_context(renew_status),
                body_text_content=self.__get_test_text_context(renew_status)
            )
            partial_results.append(partial_result)

        return MailResultMerger.merge(partial_results)

    def notify(self) -> MailNotifierResult:
        return self.__notify(self.__get_emails())

    def __notify(self, emails: list[str]) -> MailNotifierResult:
        return Mailer.send_template_mail(
            bcc_recipients=emails, subject=self.MAIL_SUBJECT,  body_html_template=self.MAIL_TEMPLATE,
            body_html_context=self.__get_template_context(), body_text_content=self.__get_text_content()
        )

    def __get_template_context(self):
        return {
            'course': str(self.course),
            'pay_date': self.pay_date,
            'pay_amount': self.pay_amount,
        }

    def __get_text_content(self, account_last_4_digits: str, pay_amount) -> str:
        if self.notify_type == self.TYPE_ENROLLMENT:
            return (
                f'En los próximos días te cobraremos la matrícula de las extraescolares del curso {self.course}. \n'
                f'- La cuenta de cobro acaba en: {account_last_4_digits}. \n'
                f'- Fecha de cobro: {self.pay_date}. \n'
                f'- Importe: {pay_amount}. \n'
                f'\n\n'
                f'Datozen egunetan {self.course} ikasturteko eskolaz kanpoko matrikulak kobratuko dizkizugu. \n'
                f'- Kobrantza-kontua horrela amaitzen da: {account_last_4_digits}. \n'
                f'- Kobrantza-data: {self.pay_date}. \n'
                f'- Zenbateko: {self.pay_amount}. \n'
            )
        elif self.notify_type == self.TYPE_FIRST_FEE:
            return (
                f'En los próximos días te cobraremos la primera cuota de las extraescolares del curso {self.course}. \n'
                f'- La cuenta de cobro acaba en: {account_last_4_digits}. \n'
                f'- Fecha de cobro: {self.pay_date}. \n'
                f'- Importe: {self.pay_amount}. \n'
                f'\n\n'
                f'Datozen egunetan {self.course} ikasturteko eskolaz kanpoko lehen kuota kobratuko dizugu. \n'
                f'- Kobrantza-kontua horrela amaitzen da: {account_last_4_digits}. \n'
                f'- Kobrantza-data: {self.pay_date}. \n'
                f'- Zenbateko: {self.pay_amount}. \n'
            )
        elif self.notify_type == self.TYPE_LAST_FEE:
            return (
                f'En los próximos días te cobraremos la última cuota de las extraescolares del curso {self.course}. \n'
                f'- La cuenta de cobro acaba en: {account_last_4_digits}. \n'
                f'- Fecha de cobro: {self.pay_date}. \n'
                f'- Importe: {self.pay_amount}. \n'
                f'\n\n'
                f'Datozen egunetan {self.course} ikasturteko eskolaz kanpoko azken kuota kobratuko dizugu. \n'
                f'- Kobrantza-kontua horrela amaitzen da: {account_last_4_digits}. \n'
                f'- Kobrantza-data: {self.pay_date}. \n'
                f'- Zenbateko: {self.pay_amount}. \n'
            )
        else:
            return gettext_lazy('Unknown renew status')

    def __get_formatted_pay_date(self) -> str:
        return date_format(self.remittance.payment_date, "l, j \\d\\e F")

    def __get_formatted_pay_amount(self) -> str:
        fee: Fee = Fee.objects.get(academic_course=self.remittance.course)
        return f'{fee.amount} €'

    def __get_emails(self) -> list[str]:
        self.emails = []
        for receipt in self.remittance.receipts.all():
            self.__append_email(receipt.family.email)
            self.__append_email(receipt.family.secondary_email)
        return self.emails

    def __append_email(self, email: str):
        if email and email not in self.emails:
            self.emails.append(email)
