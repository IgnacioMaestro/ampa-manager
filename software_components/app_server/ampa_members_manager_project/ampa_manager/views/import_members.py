from django.shortcuts import render


def render_members_import(request):
    context = {}
    return render(request, 'import_members.html', context)

def import_members(request):
    context = {}
    return render(request, 'import_members.html', context)
