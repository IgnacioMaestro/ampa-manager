from django.shortcuts import render
from django.urls import reverse

from ampa_manager.activity.use_cases.importers.after_school_activities_importer import AfterSchoolsActivitiesImporter
from ampa_manager.activity.use_cases.importers.after_school_registrations_importer import \
    AfterSchoolsRegistrationsImporter
from ampa_manager.forms import ImportAfterSchoolsRegistrationsForm, ImportAfterSchoolsActivitiesForm
from ampa_manager.utils.excel.importers_utils import get_excel_columns


def import_after_schools_registrations(request):
    success = None
    results = None
    summary = None

    if request.method == 'POST':
        form = ImportAfterSchoolsRegistrationsForm(request.POST, request.FILES)
        if form.is_valid():
            total_rows, success_rows, summary, results = \
                AfterSchoolsRegistrationsImporter.import_after_schools_registrations(file_content=request.FILES['file'].read())
            success = total_rows > 0 and total_rows == success_rows
    else:
        form = ImportAfterSchoolsRegistrationsForm()

    context = {
        'form': form,
        'success': success,
        'import_results': results,
        'import_summary': summary,
        'excel_columns': get_excel_columns(AfterSchoolsRegistrationsImporter.COLUMNS_TO_IMPORT),
        'form_action': reverse('import_after_schools_registrations'),
        'excel_template_file_name': 'templates/plantilla_importar_inscripciones_extraescolares.xls'
    }
    return render(request, 'import_after_schools_registrations.html', context)


def import_after_schools_activities(request):
    success = None
    results = None
    summary = None

    if request.method == 'POST':
        form = ImportAfterSchoolsActivitiesForm(request.POST, request.FILES)
        if form.is_valid():
            total_rows, success_rows, summary, results = \
                AfterSchoolsActivitiesImporter.import_after_schools_activities(file_content=request.FILES['file'].read())
            success = total_rows > 0 and total_rows == success_rows
    else:
        form = ImportAfterSchoolsActivitiesForm()

    context = {
        'form': form,
        'success': success,
        'import_results': results,
        'import_summary': summary,
        'excel_columns': get_excel_columns(AfterSchoolsActivitiesImporter.COLUMNS_TO_IMPORT),
        'form_action': reverse('import_after_schools_activities'),
        'excel_template_file_name': 'templates/plantilla_importar_actividades_extraescolares.xls'
    }
    return render(request, 'import_after_schools_activities.html', context)
