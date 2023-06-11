from django.urls import path

from ampa_manager.views.check_members import check_members
from ampa_manager.views.import_after_schools_activities import ImportAfterSchoolsActivities
from ampa_manager.views.import_after_schools_registrations import ImportAfterSchoolsRegistrations
from ampa_manager.views.import_custody import ImportCustodyView
from ampa_manager.views.import_members import ImportMembers
from ampa_manager.views.validate_data import validate_families_data

urlpatterns = [
    path('members/import/', ImportMembers.as_view(), name='import_members'),
    path('members/check/', check_members, name='check_members'),
    path(
        'afterschools-registrations/import/', ImportAfterSchoolsRegistrations.as_view(),
        name='import_after_schools_registrations'),
    path(
        'afterschools-activities/import/', ImportAfterSchoolsActivities.as_view(),
        name='import_after_schools_activities'),
    path('custody/import/', ImportCustodyView.as_view(), name='import_custody'),
    path('validations/family/', validate_families_data, name='validate_data'),
]
