from django.shortcuts import render

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.use_cases.importers.custody_importer import CustodyImporter
from ampa_manager.forms import ImportCustodyForm
from ampa_manager.utils.importers_utils import get_excel_columns


def import_custody(request):
    import_log = None

    if request.method == 'POST':
        form = ImportCustodyForm(request.POST, request.FILES)
        if form.is_valid():
            edition_id = request.POST.get('custody_edition')
            custody_edition = CustodyEdition.objects.get(id=edition_id)
            logs = CustodyImporter.import_custody(file_content=request.FILES['file'].read(),
                                                  custody_edition=custody_edition)
            import_log = '\n'.join(logs)
    else:
        form = ImportCustodyForm()

    context = {
        'form': form,
        'import_log': import_log,
        'excel_columns': get_excel_columns(CustodyImporter.COLUMNS_TO_IMPORT),
        'form_action': '/ampa/custody/import/',
        'excel_template_file_name': 'templates/plantilla_importar_ludoteca.xls'
    }
    return render(request, 'import_custody.html', context)
