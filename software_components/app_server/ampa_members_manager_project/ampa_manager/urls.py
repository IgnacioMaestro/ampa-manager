from django.urls import path, include

from ampa_manager.views.importers.import_after_school_activities_view import ImportAfterSchoolActivitiesView
from ampa_manager.views.importers.import_after_school_registrations_view import ImportAfterSchoolRegistrationsView
from ampa_manager.views.importers.import_camps_view import ImportCampsView
from ampa_manager.views.importers.import_custody_view import ImportCustodyView
from ampa_manager.views.membership_campaign.generate_members_remittance_view import GenerateMembersRemittanceView
from ampa_manager.views.membership_campaign.import_last_course_members_view import ImportLastCourseMembersView
from ampa_manager.views.membership_campaign.import_new_members_view import ImportNewMembersView
from ampa_manager.views.membership_campaign.notify_membership_campaign_view import NotifyMembershipCampaignView
from ampa_manager.views.membership_campaign.notify_membership_remittance_view import NotifyMembersRemittanceView
from ampa_manager.views.membership_campaign.open_membership_campaign_view import OpenMembershipCampaignView
from ampa_manager.views.validate_data import validate_data

membership_campaign_urlpatterns = [
    path('notify/', NotifyMembershipCampaignView.as_view(), name='notify_members_campaign'),
    path('open/', OpenMembershipCampaignView.as_view(), name='open_members_campaign'),
    path('import-new-members/', ImportNewMembersView.as_view(), name='import_new_members'),
    path('import-last-course-members/', ImportLastCourseMembersView.as_view(), name='import_last_course_members'),
    path('generate-remittance/', GenerateMembersRemittanceView.as_view(), name='generate_members_remittance'),
    path('notify-remittance/', NotifyMembersRemittanceView.as_view(), name='notify_members_remittance'),
]

urlpatterns = [
    path('custody/import/', ImportCustodyView.as_view(), name='import_custody'),
    path('camps/import/', ImportCampsView.as_view(), name='import_camps'),
    path('members-campaign/', include(membership_campaign_urlpatterns)),
    path('afterschools-registrations/import/', ImportAfterSchoolRegistrationsView.as_view(),
         name='import_after_schools_registrations'),
    path('afterschools-activities/import/', ImportAfterSchoolActivitiesView.as_view(),
         name='import_after_schools_activities'),
    path('validations/', validate_data, name='validate_data'),
]
