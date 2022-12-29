from django.core.management.base import BaseCommand

from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.parent import Parent


class Command(BaseCommand):
    help = 'Fix surnames in families, parents and children. Remove duplicated children.'

    def handle(self, *args, **options):
        Family.remove_duplicated_children()
        Family.fix_surnames()
        Parent.fix_name_and_surnames()
        Child.fix_names()
