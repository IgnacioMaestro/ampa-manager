from django.urls import path

from ampa_manager.views.check_members import check_members
from ampa_manager.views.import_members import import_members
from ampa_manager.views.import_custody import import_custody
from ampa_manager.views.import_after_schools import  import_after_schools

urlpatterns = [
    path('members/import/', import_members, name='import_members'),
    path('members/check/', check_members, name='check_members'),
    path('afterschools/import/', import_after_schools, name='import_custody'),
    path('custody/import/', import_custody, name='import_after_schools'),
]
