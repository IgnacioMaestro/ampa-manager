import xlrd

from django.http import HttpResponse
from django.shortcuts import render
from xlrd import Book
from xlrd.sheet import Sheet

from ampa_manager.family.models.family import Family
from ampa_manager.family.models.membership import Membership
from ampa_manager.forms import CheckMembersForm


def check_members(request):

    if request.method == 'POST':
        excel_file = request.FILES['file']
        book = xlrd.open_workbook(file_contents=excel_file.read())
        sheet = book.sheet_by_index(0)

        set_member_header(sheet)
        for row_index in range(1, sheet.nrows):
            is_member = check_is_member(sheet, row_index)
            set_member_value(sheet, row_index, is_member)

        return prepare_response(book)

    context = {
        'form': CheckMembersForm(),
        'form_action': '/ampa/members/check/',
        'excel_template_file_name': 'plantilla_consultar_socios.xls'
    }
    return render(request, 'check_members.html', context)


def prepare_response(book: Book) -> HttpResponse:
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="socios.xls"'

    # book.save(response)
    # return response

    for sheet_index in range(book.nsheets):
        sheet = book.sheet_by_index(sheet_index)

        for row_index in range(sheet.nrows):
            row = sheet.row(row_index)

            for col_index, cell in enumerate(row):
                response.write(cell.value)

    return response


def set_member_header(sheet: Sheet):
    sheet.put_cell(0, sheet.ncols, xlrd.XL_CELL_TEXT, 'La familia es socia', None)


def set_member_value(sheet: Sheet, row_index: int, is_member: bool):
    value = 'SI' if is_member else 'NO'
    sheet.put_cell(row_index, sheet.ncols, xlrd.XL_CELL_TEXT, value, None)


def check_is_member(sheet: Sheet, row_index: int) -> bool:
    family_surnames = sheet.cell_value(rowx=row_index, colx=0)
    parent1_full_name = sheet.cell_value(rowx=row_index, colx=1)
    parent2_full_name = sheet.cell_value(rowx=row_index, colx=2)
    # children_names = sheet.cell_value(rowx=row_index, colx=3)
    family, error = Family.find(family_surnames, [parent1_full_name, parent2_full_name])
    if family:
        return Membership.is_member_family(family)
    return False
