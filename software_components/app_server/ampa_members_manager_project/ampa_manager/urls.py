from django.urls import path

from ampa_manager.views.import_members import import_members, render_members_import
from ampa_manager.views.import_custody import import_custody, render_custody_import
from ampa_manager.views.import_after_schools import  import_after_schools, render_after_schools_import

urlpatterns = [
    path('import/members/page/', render_members_import, name='render_members_import'),
    path('import/afterschools/page/', render_after_schools_import, name='render_after_schools_import'),
    path('import/custody/page/', render_custody_import, name='render_custody_import'),
    path('import/members/run/', import_members, name='import_members_run'),
    path('import/afterschools/run/', import_after_schools, name='import_after_schools_run'),
    path('import/custody/run/', import_custody, name='import_custody_run'),
]
