from django.shortcuts import render
from django.urls import reverse
from django.views import View

from ampa_manager.activity.use_cases.importers.base_importer import BaseImporter
from ampa_manager.activity.use_cases.old_importers.after_school_activities_importer import \
    AfterSchoolsActivitiesImporter
from ampa_manager.forms import ImportAfterSchoolsActivitiesForm
from ampa_manager.views.import_info import ImportInfo


class ImportAfterSchoolsActivities(View):
    TEMPLATE = 'import_after_schools_activities.html'

    @classmethod
    def post(cls, request):
        form = ImportAfterSchoolsActivitiesForm(request.POST, request.FILES)
        if form.is_valid():
            file_content = request.FILES['file'].read()
            import_info: ImportInfo = AfterSchoolsActivitiesImporter.import_activities(file_content=file_content)
            context = cls.__create_context_with_import_info(form, import_info)
        else:
            context = cls.__create_context_with_processed_form(form)
        return render(request, cls.TEMPLATE, context)

    @classmethod
    def get(cls, request):
        context = cls.__create_context_with_empty_form()
        return render(request, cls.TEMPLATE, context)

    @classmethod
    def __create_context_with_import_info(cls, form: ImportAfterSchoolsActivitiesForm, import_info: ImportInfo) -> dict:
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
        return cls.__create_context_with_form(ImportAfterSchoolsActivitiesForm())

    @classmethod
    def __create_context_with_form(cls, form) -> dict:
        context = {'form': form}
        context.update(cls.__create_context_fix_part())
        return context

    @classmethod
    def __create_context_fix_part(cls) -> dict:
        return {
            'excel_columns': BaseImporter.get_excel_columns(AfterSchoolsActivitiesImporter.COLUMNS_TO_IMPORT),
            'form_action': reverse('import_after_schools_activities'),
            'excel_template_file_name': 'templates/plantilla_importar_actividades_extraescolares.xls'
        }
