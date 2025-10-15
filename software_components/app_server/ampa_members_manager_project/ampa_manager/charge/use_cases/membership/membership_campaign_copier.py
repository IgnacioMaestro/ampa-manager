from ampa_manager.family.models.family import Family
from ampa_manager.family.models.membership import Membership


class MembershipCampaignCopier:

    def copy_members_from_last_course(self):
        for family in Family.objects.membership_renew():
            Membership.make_member_for_active_course(family)
