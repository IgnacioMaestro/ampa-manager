from django.conf import settings

from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.charge.use_cases.membership.mail_notifier_result import MailNotifierResult
from ampa_manager.family.models.membership import Membership
from ampa_manager.utils.mailer import Mailer


class MembershipWelcomeNotifier:
    MAIL_SUBJECT = 'Bienvenida de socios | Bazkideen ongi etorria'
    MAIL_TEMPLATE = 'emails/membership_welcome_email.html'

    def __init__(self, is_a_test: bool = False):
        self.course: AcademicCourse = ActiveCourse.load()
        self.is_a_test = is_a_test

    def notify(self) -> MailNotifierResult:
        emails = self.__get_recipient_emails()
        if not emails:
            return MailNotifierResult()

        return Mailer.send_template_mail(
            bcc_recipients=emails,
            subject=self.MAIL_SUBJECT,
            body_html_template=self.MAIL_TEMPLATE,
            body_html_context=self.__get_template_context(),
            body_text_content=self.__get_text_content()
        )

    def __get_recipient_emails(self) -> list[str]:
        if self.is_a_test:
            return [settings.TEST_EMAIL_RECIPIENT]

        emails: list[str] = []
        memberships = Membership.objects.of_course(self.course).select_related('family')
        for membership in memberships:
            self.__append_email(emails, membership.family.email)
            self.__append_email(emails, membership.family.secondary_email)
        return emails

    @staticmethod
    def __append_email(emails: list[str], email: str):
        if email and email not in emails:
            emails.append(email)

    def __get_template_context(self):
        return {
            'course': str(self.course),
            'info_email': settings.INFO_EMAIL,
            'whatsapp_community_url': settings.WHATSAPP_COMMUNITY_URL,
            'website_url': settings.WEBSITE_URL,
            'website_label': settings.WEBSITE_LABEL,
            'committees_url': settings.COMMITTEES_URL,
        }

    def __get_text_content(self) -> str:
        info_email = settings.INFO_EMAIL
        whatsapp_community_url = settings.WHATSAPP_COMMUNITY_URL
        website_url = settings.WEBSITE_URL
        website_label = settings.WEBSITE_LABEL
        committees_url = settings.COMMITTEES_URL
        return (
            f'Os damos la bienvenida como socios de la AFA para el curso {self.course}. '
            f'\n\n'
            f'- Si tienes alguna duda puedes escribir a {info_email}. \n'
            f'- Tenemos una comunidad de whatsapp ({whatsapp_community_url}) donde ponemos avisos importantes. \n'
            f'- Puedes consultar la web {website_label} ({website_url}) para apuntarte en actividades, consultar información '
            f'o ver la lista de comisiones ({committees_url}). '
            f'Si crees que puedes colaborar en alguna de ellas serás bienvenido/a. Todos los que colaboramos somos padres y madres como tú. \n'
            f'- Hay una reunión mensual para tratar los temas activos y cualquier sugerencia. Avisamos de las fechas en la comunidad de whatsapp. \n'
            f'\n'
            f'Gracias por formar parte de la Asociación de Familias del Alumnado. \n'
            f'\n\n'
            f'Ongi etorri IFEko bazkide gisa {self.course} ikasturterako. '
            f'\n\n'
            f'- Zalantzarik baduzu, idatzi {info_email} helbidera. \n'
            f'- Whatsapp komunitate bat dugu ({whatsapp_community_url}), eta bertan abisu garrantzitsuak jartzen ditugu. \n'
            f'- {website_label} ({website_url}) webgunea kontsulta dezakezu jardueretan izena emateko, informazioa kontsultatzeko '
            f'edo batzordeen zerrenda ({committees_url}) ikusteko. '
            f'Haietako batean lagun dezakezula uste baduzu, ongi etorria izango zara. Laguntzen dugunok zu bezalako gurasoak gara. \n'
            f'- Hilean behin bilera bat dago gai aktiboak eta edozein iradokizun lantzeko. Datak whatsapp komunitatean jakinarazten ditugu. \n'
            f'\n'
            f'Eskerrik asko Ikasleen Familia Elkarteko parte izateagatik. \n'
        )
