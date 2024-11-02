from django.urls import path

from ampa_manager.views.check_family_email import CheckFamilyEmail
from ampa_manager.views.check_members import MemberChecker
from ampa_manager.views.import_afterschool_registrations import ImportAfterSchoolRegistrations
from ampa_manager.views.import_camps import ImportCamps
from ampa_manager.views.import_custody import ImportCustody
from ampa_manager.views.import_family_email import ImportFamilyEmail
from ampa_manager.views.import_members import ImportMembers
from ampa_manager.views.validate_data import validate_data

urlpatterns = [
    path('members/check/', MemberChecker.as_view(), name='check_members'),
    path('family-email/import/', ImportFamilyEmail.as_view(), name='import_family_email'),
    path('family-email/check/', CheckFamilyEmail.as_view(), name='check_family_email'),
    path('custody/import/', ImportCustody.as_view(), name='import_custody'),
    path('camps/import/', ImportCamps.as_view(), name='import_camps'),
    path('members/import/', ImportMembers.as_view(), name='import_members'),
    path('afterschools-registrations/import/', ImportAfterSchoolRegistrations.as_view(),
         name='import_after_schools_registrations'),
    # path('afterschools-activities/import/', ImportAfterSchoolsActivities.as_view(),
    #      name='import_after_schools_activities'),
    path('validations/', validate_data, name='validate_data'),
]
