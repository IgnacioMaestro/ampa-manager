from django.core.management.base import BaseCommand

from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.parent import Parent


class Command(BaseCommand):
    help = 'Normalize family, parents and children names and surnames'

    def handle(self, *args, **options):
        family_count = Family.objects.count()
        num = 1
        for family in Family.objects.all():
            family.save()
            print(f'Family {num}/{family_count} normalized')
            num += 1

        family_count = Parent.objects.count()
        num = 1
        for parent in Parent.objects.all():
            parent.save()
            print(f'Parent {num}/{family_count} normalized')
            num += 1

        family_count = Child.objects.count()
        num = 1
        for child in Child.objects.all():
            child.save()
            print(f'Child {num}/{family_count} normalized')
            num += 1
