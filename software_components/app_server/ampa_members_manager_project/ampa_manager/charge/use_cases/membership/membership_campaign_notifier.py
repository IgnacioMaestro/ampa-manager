from django.conf import settings
from django.utils.translation import gettext

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.use_cases.membership.mail_notifier_result import MailNotifierResult
from ampa_manager.charge.use_cases.membership.mail_result_merger import MailResultMerger
from ampa_manager.family.models.family import Family
from ampa_manager.utils.mailer import Mailer


class MembershipCampaignNotifier:
    MAIL_SUBJECT = 'Campaña de socios | Bazkideen kanpaina'
    MAIL_TEMPLATE = 'emails/membership_campaign_email.html'
    RENEW_STATUS_RENEW = 'RENEW'
    RENEW_STATUS_NO_RENEW_NO_SCHOOL_CHILDREN = 'NO_RENEW_NO_SCHOOL_CHILDREN'
    RENEW_STATUS_DECLINED = 'NO_RENEW_DECLINED'

    def __init__(self, is_a_test: bool = False):
        self.course: AcademicCourse = ActiveCourse.load()
        self.is_a_test = is_a_test

    def notify(self) -> MailNotifierResult:
        partial_results = []
        for renew_status, families in self.__get_families_by_renew_status().items():
            emails = self.__get_recipient_emails(families)
            if not emails:
                continue
            partial_results.append(Mailer.send_template_mail(
                bcc_recipients=emails,
                subject=self.MAIL_SUBJECT,
                body_html_template=self.MAIL_TEMPLATE,
                body_html_context=self.__get_template_context(renew_status),
                body_text_content=self.__get_text_content(renew_status)
            ))

        return MailResultMerger.merge(partial_results)

    def __get_families_by_renew_status(self) -> dict:
        return {
            self.RENEW_STATUS_RENEW: Family.objects.membership_renew(),
            self.RENEW_STATUS_NO_RENEW_NO_SCHOOL_CHILDREN: Family.objects.membership_no_renew_no_school_children(),
            self.RENEW_STATUS_DECLINED: Family.objects.membership_no_renew_declined(),
        }

    def __get_recipient_emails(self, families) -> list[str]:
        if self.is_a_test:
            return [settings.TEST_EMAIL_RECIPIENT]

        emails: list[str] = []
        for family in families:
            self.__append_email(emails, family.email)
            self.__append_email(emails, family.secondary_email)
        return emails

    @staticmethod
    def __append_email(emails: list[str], email: str):
        if email and email not in emails:
            emails.append(email)

    def __get_template_context(self, renew_status: str):
        return {
            'course': str(self.course),
            'renew_status': renew_status,
        }

    def __get_text_content(self, renew_status: str) -> str:
        if renew_status == self.RENEW_STATUS_RENEW:
            return (
                f'Iniciamos la campaña de socios para este curso {self.course}. '
                f'\n\n'
                f'Según los datos que tenemos, el año pasado vuestra familia fue socia y vuestros hijos/as siguen en la ikastola. '
                f'Este año se os volverá a pasar la cuota. \n'
                f'- Si queréis seguir siendo socio: no tenéis que hacer nada. \n'
                f'- Si no queréis renovar o queréis cambiar el nº de cuenta: responded a este correo para que lo corrijamos. \n'
                f'\n\n'
                f'{self.course} ikasturte honetarako bazkide kanpaina hasiko dugu.'
                f'\n\n'
                f'Ditugun datuen arabera, iaz zuen familia bazkide izan zen eta zuen seme-alabek ikastolan jarraitzen dute. '
                f'Aurten, kuota berriro pasatuko zaizue. \n'
                f'- Bazkide izaten jarraitu nahi baduzue: ez duzue ezer egin behar. \n'
                f'- Ez baduzue berritu nahi edo kontu-zenbakia aldatu nahi baduzue: erantzun mezu honi zuzen dezagun. \n'
            )
        elif renew_status == self.RENEW_STATUS_NO_RENEW_NO_SCHOOL_CHILDREN:
            return (
                f'Iniciamos la campaña de socios para este curso {self.course}. '
                f'\n\n'
                f'Según los datos que tenemos, el año pasado vuestra familia fue socia, pero este año vuestros hijos/as ya no están en la ikastola. '
                f'Por eso este año no os vamos a cobrar la cuota de socio. \n'
                f'- Si esto es correcto: no tenéis que hacer nada. \n'
                f'- Si esto no es correcto y queréis seguir siendo socios: responded a este correo para que lo corrijamos. \n'
                f'\n\n'
                f'{self.course} ikasturte honetarako bazkide kanpaina hasiko dugu.'
                f'\n\n'
                f'Ditugun datuen arabera, iaz zuen familia bazkide izan zen, baina aurten zuen seme-alabak jada ez daude ikastolan. Horregatik, '
                f'aurten ez dizuegu bazkide-kuota kobratuko \n'
                f'- Hori zuzena bada: ez duzue ezer egin behar. \n'
                f'- Hori zuzena ez bada eta bazkide izaten jarraitu nahi baduzue: erantzun mezu honi zuzen dezagun. \n'
            )
        elif renew_status == self.RENEW_STATUS_DECLINED:
            return (
                f'Iniciamos la campaña de socios para este curso {self.course}. '
                f'\n\n'
                f'Según los datos que tenemos, el año pasado vuestra familia fue socia, pero habéis solicitado no renovar. '
                f'Por eso este año no os vamos a cobrar la cuota de socio. \n'
                f'- Si esto es correcto: no tenéis que hacer nada. \n'
                f'- Si esto no es correcto y queréis seguir siendo socios: responded a este correo para que lo corrijamos. \n'
                f'\n\n'
                f'{self.course} ikasturte honetarako bazkide kanpaina hasiko dugu.'
                f'\n\n'
                f'Ditugun datuen arabera, iaz zuen familia bazkide izan zen, baina ez berritzea eskatu duzue. '
                f'Horregatik, aurten ez dizuegu bazkide-kuota kobratuko. \n'
                f'- Hori zuzena bada: ez duzue ezer egin behar. \n'
                f'- Hori zuzena ez bada eta bazkide izaten jarraitu nahi baduzue: erantzun mezu honi zuzen dezagun. \n'
            )
        else:
            return gettext('Unknown renew status')
