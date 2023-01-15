from django.shortcuts import render


def render_custody_import(request):
    context = {}
    return render(request, 'import_custody.html', context)

def import_custody(request):
    context = {}
    return render(request, 'import_custody.html', context)
