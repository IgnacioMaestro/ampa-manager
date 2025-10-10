from django.urls import path

from ampa_manager.views.generate_remittance.generate_members_remittance_view import GenerateMembersRemittanceView
from ampa_manager.views.importers.import_after_school_activities_view import ImportAfterSchoolActivitiesView
from ampa_manager.views.importers.import_after_school_registrations_view import ImportAfterSchoolRegistrationsView
from ampa_manager.views.importers.import_camps_view import ImportCampsView
from ampa_manager.views.importers.import_custody_view import ImportCustodyView
from ampa_manager.views.importers.import_members_view import ImportMembersView
from ampa_manager.views.notifiers.notify_membership_campaign_view import NotifyMembershipCampaignView
from ampa_manager.views.notifiers.notify_membership_remittance_view import NotifyMembersRemittanceView
from ampa_manager.views.validate_data import validate_data

urlpatterns = [
    path('custody/import/', ImportCustodyView.as_view(), name='import_custody'),
    path('camps/import/', ImportCampsView.as_view(), name='import_camps'),
    path('members/import/', ImportMembersView.as_view(), name='import_members'),
    path('members-campaign/notify/', NotifyMembershipCampaignView.as_view(), name='notify_members_campaign'),
    path('membership-remittances/generate/', GenerateMembersRemittanceView.as_view(), name='generate_members_remittance'),
    path('membership-remittances/<int:remittance_id>/notify/', NotifyMembersRemittanceView.as_view(), name='notify_members_remittance'),
    path('afterschools-registrations/import/', ImportAfterSchoolRegistrationsView.as_view(),
         name='import_after_schools_registrations'),
    path('afterschools-activities/import/', ImportAfterSchoolActivitiesView.as_view(),
         name='import_after_schools_activities'),
    path('validations/', validate_data, name='validate_data'),
]
