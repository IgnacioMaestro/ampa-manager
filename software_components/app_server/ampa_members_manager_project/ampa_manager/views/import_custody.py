from django.shortcuts import render


def import_custody(request):
    context = {}
    return render(request, 'import_custody.html', context)
