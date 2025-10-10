from typing import Optional

from django.utils.translation import gettext_lazy

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.use_cases.membership.families_notifier_result import FamiliesNotifierResult
from ampa_manager.family.models.family import Family
from ampa_manager.utils.mailer import Mailer


class MembershipCampaignNotifier:
    MAIL_SUBJECT = 'Campaña de socios | Bazkideen kanpaina'
    MAIL_TEMPLATE = 'emails/membership_campaign_email.html'
    RENEW_STATUS_RENEW = 'RENEW'
    RENEW_STATUS_NO_RENEW_NO_SCHOOL_CHILDREN = 'NO_RENEW_NO_SCHOOL_CHILDREN'
    RENEW_STATUS_DECLINED = 'NO_RENEW_DECLINED'

    def __init__(self):
        self.course: AcademicCourse = ActiveCourse.load()
        self.notified_families: list[int] = []

    def notify(self) -> FamiliesNotifierResult:
        families = {
            self.RENEW_STATUS_RENEW: Family.objects.membership_renew(),
            self.RENEW_STATUS_NO_RENEW_NO_SCHOOL_CHILDREN: Family.objects.membership_no_renew_no_school_children(),
            self.RENEW_STATUS_DECLINED: Family.objects.membership_no_renew_declined(),
        }

        for renew_status, families in families.items():
            for family in families:
                error: Optional[str] = Mailer.send_template_mail(
                    to_recipients=self.__get_emails(family),
                    subject=self.MAIL_SUBJECT,
                    body_html_template=self.MAIL_TEMPLATE,
                    body_html_context=self.__get_template_context(family, renew_status),
                    body_text_content=self.__get_text_content(family, renew_status)
                )
                if error:
                    return FamiliesNotifierResult(self.notified_families, family, error)
                else:
                    self.notified_families.append(family.id)
        return FamiliesNotifierResult(self.notified_families)

    def __get_template_context(self, family: Family, renew_status: str):
        return {
            'course': str(self.course),
            'account_last_4_digits': self.__get_membership_account_last_4_digits(family),
            'renew_status': renew_status,
        }

    def __get_text_content(self, family: Family, renew_status: str) -> str:
        account_last_4_digits = self.__get_membership_account_last_4_digits(family)
        if renew_status == self.RENEW_STATUS_RENEW:
            return (
                f'Próximamente iniciamos la campaña de socios para este curso {self.course}. '
                f'\n\n'
                f'Según los datos que tenemos, el año pasado vuestra familia fue socia y vuestros hijos/as siguen en la ikastola. '
                f'Este año se os volverá a pasar la cuota a la cuenta terminada en {account_last_4_digits}. \n'
                f'- Si queréis seguir siendo socio: no tenéis que hacer nada. \n'
                f'- Si no queréis renovar o queréis cambiar el nº de cuenta: responded a este correo para que lo corrijamos. \n'
                f'\n\n'
                f'Ditugun datuen arabera, iaz zuen familia bazkide izan zen eta zuen seme-alabek ikastolan jarraitzen dute. '
                f'Aurten, kuota {account_last_4_digits} zenbakitan amaitutako kontura pasatuko zaizue berriro \n'
                f'- Bazkide izaten jarraitu nahi baduzue: ez duzue ezer egin behar. \n'
                f'- Ez baduzue berritu nahi edo kontu-zenbakia aldatu nahi baduzue: erantzun mezu honi zuzen dezagun. \n'
            )
        elif renew_status == self.RENEW_STATUS_NO_RENEW_NO_SCHOOL_CHILDREN:
            return (
                f'Próximamente iniciamos la campaña de socios para este curso {self.course}. '
                f'\n\n'
                f'Según los datos que tenemos, el año pasado vuestra familia fue socia, pero este año vuestros hijos/as ya no están en la ikastola. '
                f'Por eso este año no os vamos a cobrar la cuota de socio. \n'
                f'- Si esto es correcto: no tenéis que hacer nada. \n'
                f'- Si esto no es correcto y queréis seguir siendo socios: responded a este correo para que lo corrijamos. \n'
                f'\n\n'
                f'Ditugun datuen arabera, iaz zuen familia bazkide izan zen, baina aurten zuen seme-alabak jada ez daude ikastolan. Horregatik, '
                f'aurten ez dizuegu bazkide-kuota kobratuko \n'
                f'- Hori zuzena bada: ez duzue ezer egin behar. \n'
                f'- Hori zuzena ez bada eta bazkide izaten jarraitu nahi baduzue: erantzun mezu honi zuzen dezagun. \n'
            )
        elif renew_status == self.RENEW_STATUS_DECLINED:
            return (
                f'Próximamente iniciamos la campaña de socios para este curso {self.course}. '
                f'\n\n'
                f'Según los datos que tenemos, el año pasado vuestra familia fue socia, pero habéis solicitado no renovar. '
                f'Por eso este año no os vamos a cobrar la cuota de socio. \n'
                f'- Si esto es correcto: no tenéis que hacer nada. \n'
                f'- Si esto no es correcto y queréis seguir siendo socios: responded a este correo para que lo corrijamos. \n'
                f'\n\n'
                f'Ditugun datuen arabera, iaz zuen familia bazkide izan zen, baina ez berritzea eskatu duzue. '
                f'Horregatik, aurten ez dizuegu bazkide-kuota kobratuko. \n'
                f'- Hori zuzena bada: ez duzue ezer egin behar. \n'
                f'- Hori zuzena ez bada eta bazkide izaten jarraitu nahi baduzue: erantzun mezu honi zuzen dezagun. \n'
            )
        else:
            return gettext_lazy('Unknown renew status')

    @classmethod
    def __get_emails(cls, family: Family) -> list[str]:
        return ['danilanda@gmail.com']
        emails = []
        if family.email:
            emails.append(family.email)
        if family.secondary_email:
            emails.append(family.secondary_email)
        return emails

    def __get_membership_account_last_4_digits(self, family: Family):
        if family and family.membership_holder and family.membership_holder.bank_account and family.membership_holder.bank_account.iban:
            return family.membership_holder.bank_account.iban[-4:]
        return gettext_lazy('Not available')
