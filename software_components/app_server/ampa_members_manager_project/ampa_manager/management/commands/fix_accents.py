from django.core.management.base import BaseCommand

from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.parent import Parent


class Command(BaseCommand):
    help = 'Fix accents in families, parents and children'

    def handle(self, *args, **options):
        Family.fix_accents()
        Parent.fix_accents()
        Child.fix_accents()
