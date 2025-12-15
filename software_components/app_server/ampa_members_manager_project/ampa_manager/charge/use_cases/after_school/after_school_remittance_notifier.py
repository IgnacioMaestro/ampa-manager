from django.conf import settings
from django.utils.formats import date_format
from django.utils.translation import gettext

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from ampa_manager.charge.models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ampa_manager.charge.use_cases.membership.mail_notifier_result import MailNotifierResult
from ampa_manager.utils.mailer import Mailer


class AfterSchoolRemittanceNotifier:
    MAIL_SUBJECT = 'Cuota de extraescolares | Eskolaz kanpoko kuota'
    MAIL_TEMPLATE = 'emails/after_school_remittance_email.html'
    TYPE_ENROLLMENT = 'ENROLLMENT'
    TYPE_FIRST_FEE = 'FIRST_FEE'
    TYPE_LAST_FEE = 'LAST_FEE'

    def __init__(self, remittance: AfterSchoolRemittance, notify_type: str):
        self.notify_type: str = notify_type
        self.remittance: AfterSchoolRemittance = remittance
        self.course: AcademicCourse = ActiveCourse.load()
        self.pay_date: str = self.__get_formatted_pay_date()

    def test_notify(self) -> MailNotifierResult:
        return Mailer.send_template_mail(
            bcc_recipients=[settings.TEST_EMAIL_RECIPIENT],
            subject=self.MAIL_SUBJECT,
            body_html_template=self.MAIL_TEMPLATE,
            body_html_context=self.__get_test_template_context(),
            body_text_content=self.__get_test_text_context()
        )

    def notify(self) -> MailNotifierResult:
        return Mailer.send_template_mail(
            bcc_recipients=self.__get_remittance_emails(),
            subject=self.MAIL_SUBJECT,
            body_html_template=self.MAIL_TEMPLATE,
            body_html_context=self.__get_template_context(),
            body_text_content=self.__get_text_content()
        )

        # partial_results = []
        #
        # for receipt in self.remittance.receipts.all():
        #     partial_result: MailNotifierResult = Mailer.send_template_mail(
        #         bcc_recipients=self.get_receipt_emails(receipt),
        #         subject=self.MAIL_SUBJECT,
        #         body_html_template=self.MAIL_TEMPLATE,
        #         body_html_context=self.__get_template_context(
        #             account_last_4_digits=self.get_account_last_4_digits(receipt),
        #             pay_amount=self.__get_formatted_pay_amount(receipt)
        #         ),
        #         body_text_content=self.__get_text_content(
        #             account_last_4_digits=self.get_account_last_4_digits(receipt),
        #             pay_amount=self.__get_formatted_pay_amount(receipt)
        #         )
        #     )
        #     partial_results.append(partial_result)
        #
        # return MailResultMerger.merge(partial_results)

    def __get_test_template_context(self):
        # return self.__get_template_context(account_last_4_digits='XXXX', pay_amount='100 €')
        return self.__get_template_context()

    def __get_template_context(self):
    # def __get_template_context(self, account_last_4_digits: str, pay_amount: str):
        return {
            'course': str(self.course),
            # 'account_last_digits': account_last_4_digits,
            'pay_date': self.pay_date,
            # 'pay_amount': pay_amount,
            'notify_type': self.notify_type,
        }

    def __get_test_text_context(self):
        # return self.__get_text_content(account_last_4_digits='XXXX', pay_amount='100 €')
        return self.__get_text_content()

    def __get_text_content(self) -> str:
    # def __get_text_content(self, account_last_4_digits: str, pay_amount: str) -> str:
        if self.notify_type == self.TYPE_ENROLLMENT:
            return (
                f'En los próximos días te cobraremos la matrícula de las extraescolares del curso {self.course}. \n'
                # f'- La cuenta de cobro acaba en: {account_last_4_digits}. \n'
                f'- Fecha de cobro: {self.pay_date}. \n'
                # f'- Importe: {pay_amount}. \n'
                f'\n\n'
                f'Datozen egunetan {self.course} ikasturteko eskolaz kanpoko matrikulak kobratuko dizkizugu. \n'
                # f'- Kobrantza-kontua horrela amaitzen da: {account_last_4_digits}. \n'
                f'- Kobrantza-data: {self.pay_date}. \n'
                # f'- Zenbateko: {pay_amount}. \n'
            )
        elif self.notify_type == self.TYPE_FIRST_FEE:
            return (
                f'En los próximos días te cobraremos la primera cuota de las extraescolares del curso {self.course}. \n'
                # f'- La cuenta de cobro acaba en: {account_last_4_digits}. \n'
                f'- Fecha de cobro: {self.pay_date}. \n'
                # f'- Importe: {pay_amount}. \n'
                f'\n\n'
                f'Datozen egunetan {self.course} ikasturteko eskolaz kanpoko lehen kuota kobratuko dizugu. \n'
                # f'- Kobrantza-kontua horrela amaitzen da: {account_last_4_digits}. \n'
                f'- Kobrantza-data: {self.pay_date}. \n'
                # f'- Zenbateko: {pay_amount}. \n'
            )
        elif self.notify_type == self.TYPE_LAST_FEE:
            return (
                f'En los próximos días te cobraremos la última cuota de las extraescolares del curso {self.course}. \n'
                # f'- La cuenta de cobro acaba en: {account_last_4_digits}. \n'
                f'- Fecha de cobro: {self.pay_date}. \n'
                # f'- Importe: {pay_amount}. \n'
                f'\n\n'
                f'Datozen egunetan {self.course} ikasturteko eskolaz kanpoko azken kuota kobratuko dizugu. \n'
                # f'- Kobrantza-kontua horrela amaitzen da: {account_last_4_digits}. \n'
                f'- Kobrantza-data: {self.pay_date}. \n'
                # f'- Zenbateko: {pay_amount}. \n'
            )
        else:
            return gettext('Unknown renew status')

    def __get_formatted_pay_date(self) -> str:
        return date_format(self.remittance.payment_date, "l, j \\d\\e F")

    @classmethod
    def __get_formatted_pay_amount(cls, receipt: AfterSchoolReceipt) -> str:
        return f'{receipt.amount} €'

    @classmethod
    def __get_receipt_emails(cls, receipt) -> list[str]:
        return []
        # self.emails = []
        # for receipt in self.remittance.receipts.all():
        #     self.__append_email(receipt.family.email)
        #     self.__append_email(receipt.family.secondary_email)
        # return self.emails

    @classmethod
    def __get_account_last_4_digits(cls, receipt: AfterSchoolReceipt):
        return receipt.after_school_registration.holder.bank_account.iban[-4:]

    def __get_remittance_emails(self):
        emails = []
        for receipt in self.remittance.receipts.all():
            family = receipt.after_school_registration.child.family
            if family.email and family.email not in emails:
                emails.append(family.email)
            if family.secondary_email and family.secondary_email not in emails:
                emails.append(family.secondary_email)
        return emails
