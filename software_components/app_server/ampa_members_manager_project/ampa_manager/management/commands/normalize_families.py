from django.core.management.base import BaseCommand

from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.parent import Parent


class Command(BaseCommand):
    help = 'Normalize family, parents and children names and surnames'

    def handle(self, *args, **options):
        for family in Family.objects.all():
            family.save()
        for parent in Parent.objects.all():
            parent.save()
        for child in Child.objects.all():
            child.save()
