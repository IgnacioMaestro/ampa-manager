from django.shortcuts import render
from django.urls import reverse
from django.views import View

from ampa_manager.activity.use_cases.importers.after_school_activities_importer import AfterSchoolsActivitiesImporter
from ampa_manager.activity.use_cases.importers.after_school_registrations_importer import \
    AfterSchoolsRegistrationsImporter
from ampa_manager.forms import ImportAfterSchoolsRegistrationsForm, ImportAfterSchoolsActivitiesForm
from ampa_manager.utils.excel.importers_utils import get_excel_columns
from ampa_manager.views.import_info import ImportInfo


class ImportAfterSchoolsRegistrationsView(View):
    TEMPLATE = 'import_after_schools_registrations.html'

    @classmethod
    def post(cls, request):
        form = ImportAfterSchoolsRegistrationsForm(request.POST, request.FILES)
        if form.is_valid():
            file_content = request.FILES['file'].read()
            import_info: ImportInfo = AfterSchoolsRegistrationsImporter.import_registrations(file_content)
            context = cls.__create_context_with_import_info(form, import_info)
        else:
            context = cls.__create_context_with_processed_form(form)
        return render(request, cls.TEMPLATE, context)

    @classmethod
    def get(cls, request):
        context = cls.__create_context_with_empty_form()
        return render(request, cls.TEMPLATE, context)

    @classmethod
    def __create_context_with_import_info(cls, form: ImportAfterSchoolsRegistrationsForm,
                                          import_info: ImportInfo) -> dict:
        context = {
            'form': form,
            'success': import_info.success(),
            'import_results': import_info.results,
            'import_summary': import_info.summary,
        }
        context.update(cls.__create_context_fix_part())
        return context

    @classmethod
    def __create_context_with_processed_form(cls, form) -> dict:
        return cls.__create_context_with_form(form)

    @classmethod
    def __create_context_with_empty_form(cls) -> dict:
        return cls.__create_context_with_form(ImportAfterSchoolsRegistrationsForm())

    @classmethod
    def __create_context_with_form(cls, form) -> dict:
        context = {'form': form}
        context.update(cls.__create_context_fix_part())
        return context

    @classmethod
    def __create_context_fix_part(cls) -> dict:
        return {
            'excel_columns': get_excel_columns(AfterSchoolsRegistrationsImporter.COLUMNS_TO_IMPORT),
            'form_action': reverse('import_after_schools_registrations'),
            'excel_template_file_name': 'templates/plantilla_importar_inscripciones_extraescolares.xls'
        }


def import_after_schools_activities(request):
    success = None
    results = None
    summary = None

    if request.method == 'POST':
        form = ImportAfterSchoolsActivitiesForm(request.POST, request.FILES)
        if form.is_valid():
            total_rows, success_rows, summary, results = \
                AfterSchoolsActivitiesImporter.import_after_schools_activities(
                    file_content=request.FILES['file'].read())
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
