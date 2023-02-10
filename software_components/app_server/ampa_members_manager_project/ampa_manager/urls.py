from django.urls import path

from ampa_manager.views.import_members import import_members
from ampa_manager.views.import_custody import import_custody
from ampa_manager.views.import_after_schools import  import_after_schools

urlpatterns = [
    path('import/members/', import_members, name='import_members'),
    path('import/afterschools/', import_after_schools, name='import_custody'),
    path('import/custody/', import_custody, name='import_after_schools'),
]
