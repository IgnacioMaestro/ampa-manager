from django.urls import path

from ampa_manager.views.check_members import MemberChecker
from ampa_manager.views.import_after_schools_activities import ImportAfterSchoolsActivities
from ampa_manager.views.import_after_schools_registrations import ImportAfterSchoolsRegistrations
from ampa_manager.views.import_camps import ImportCamps
from ampa_manager.views.import_custody import ImportCustody
from ampa_manager.views.import_members import ImportMembers
from ampa_manager.views.validate_data import validate_families_data

urlpatterns = [
    path('members/import/', ImportMembers.as_view(), name='import_members'),
    path('members/check/', MemberChecker.as_view(), name='check_members'),
    path('afterschools-registrations/import/', ImportAfterSchoolsRegistrations.as_view(),
        name='import_after_schools_registrations'),
    path('afterschools-activities/import/', ImportAfterSchoolsActivities.as_view(),
         name='import_after_schools_activities'),
    path('custody/import/', ImportCustody.as_view(), name='import_custody'),
    path('camps/import/', ImportCamps.as_view(), name='import_camps'),
    path('validations/family/', validate_families_data, name='validate_data'),
]
