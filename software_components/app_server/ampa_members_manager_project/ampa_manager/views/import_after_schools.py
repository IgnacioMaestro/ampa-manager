from django.shortcuts import render


def render_after_schools_import(request):
    context = {}
    return render(request, 'import_after_schools.html', context)

def import_after_schools(request):
    context = {}
    return render(request, 'import_after_schools.html', context)
