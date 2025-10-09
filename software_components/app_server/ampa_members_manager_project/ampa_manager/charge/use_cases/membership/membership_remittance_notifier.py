import locale

from django.utils.formats import date_format

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.charge.models.fee.fee import Fee
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.utils.mailer import Mailer


class MembershipRemittanceNotifier:
    MAIL_SUBJECT = 'Cobro de la cuota de socio'
    MAIL_TEMPLATE = 'emails/membership_fee_notice.html'

    def __init__(self, remittance: MembershipRemittance):
        self.remittance: MembershipRemittance = remittance
        self.course: AcademicCourse = self.remittance.course
        self.pay_date: str = self.__get_formatted_pay_date()
        self.pay_amount: str = self.__get_formatted_pay_amount()
        self.emails: list[str] = []

    def notify(self):
        Mailer.send_template_mail(
            bcc_recipients=self.__get_emails(), subject=self.MAIL_SUBJECT,  body_html_template=self.MAIL_TEMPLATE,
            body_html_context=self.__get_template_context(), body_text_content=self.__get_text_content())

    def __get_template_context(self):
        return {
            'course': str(self.course),
            'pay_date': self.pay_date,
            'pay_amount': self.pay_amount,
        }

    def __get_text_content(self):
        return (
            f'En los próximos días te cobraremos la cuota de socio de la AFA para el curso {self.course}. \n'
            f'- Fecha de cobro: {self.pay_date}. \n'
            f'- Importe: {self.pay_amount}. \n'
            f'\n\n'
            f'Datozen egunetan AFAko bazkide kuota kobratuko dizugu {self.course} ikasturterako. \n'
            f'- Kobrantza-data: {self.pay_date}. \n'
            f'- Zenbateko: {self.pay_amount}. \n'
        )

    def __get_formatted_pay_date(self) -> str:
        return date_format(self.remittance.payment_date, "l, j \\d\\e F")

    def __get_formatted_pay_amount(self) -> str:
        fee: Fee = Fee.objects.get(academic_course=self.remittance.course)
        return f'{fee.amount} €'

    def __get_emails(self) -> list[str]:
        return ['danilanda@gmail.com']
        self.emails = []
        for receipt in self.remittance.receipts.all():
            self.__append_email(receipt.family.email)
            self.__append_email(receipt.family.secondary_email)
        return self.emails

    def __append_email(self, email: str):
        if email and email not in self.emails:
            self.emails.append(email)
