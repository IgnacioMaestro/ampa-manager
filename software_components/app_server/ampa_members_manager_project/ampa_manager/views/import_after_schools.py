from django.shortcuts import render


def import_after_schools(request):
    context = {}
    return render(request, 'import_after_schools.html', context)
