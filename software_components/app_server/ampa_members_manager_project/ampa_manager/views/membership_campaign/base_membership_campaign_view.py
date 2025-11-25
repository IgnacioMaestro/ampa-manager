from django.utils.translation import gettext_lazy as _
from django.views import View


class CampaignStep:
    def __init__(self, view_name: str, title, current: bool = False):
        self.current = current
        self.view_name = view_name
        self.title = title

    def __str__(self):
        return f'{self.title} ({self.view_name}, {self.current})'


class BaseMembershipCampaignView(View):
    CAMPAIGN_TITLE = _('Membership campaign')
    VIEW_NAME = None
    VIEW_TITLE = None
    STEPS = [
        CampaignStep(view_name='notify_members_campaign', title=_('Notify campaign')),
        CampaignStep(view_name='import_last_course_members', title=_('Import last course members')),
        CampaignStep(view_name='import_new_members', title=_('Import new members')),
        CampaignStep(view_name='generate_members_remittance', title=_('Generate remittance')),
        CampaignStep(view_name='notify_members_remittance', title=_('Notify remittance')),
    ]

    @classmethod
    def get_steps(cls) -> list[CampaignStep]:
        steps = []
        for step in cls.STEPS:
            step.current = cls.is_current_step(step.view_name)
            steps.append(step)
        return steps

    @classmethod
    def is_current_step(cls, view_name: str) -> bool:
        return view_name == cls.VIEW_NAME

    @classmethod
    def get_context(cls) -> dict:
        return {
            'steps': cls.get_steps(),
            'campaign_title': cls.CAMPAIGN_TITLE,
            'current_step_title': cls.get_current_step_title(),
        }

    @classmethod
    def get_current_step_title(cls) -> str:
        for step in cls.STEPS:
            if step.view_name == cls.VIEW_NAME:
                return step.title
        return ''
