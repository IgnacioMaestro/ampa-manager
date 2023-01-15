from django.core.management.base import BaseCommand

from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.parent import Parent


class Command(BaseCommand):
    help = 'Fix surnames in families, parents and children. Remove duplicated children.'

    def handle(self, *args, **options):
        self.find_duplicated_families()
        # Family.remove_duplicated_children()
        Family.fix_surnames()
        Parent.fix_name_and_surnames()
        self.find_duplicated_parents()
        Child.fix_names()
        self.find_duplicated_children()

    @staticmethod
    def find_duplicated_families():
        for duplicated in Family.get_duplicated_families():
            print(f'Duplicated family: {duplicated[0]} ({duplicated[0].id}) - {duplicated[1]} ({duplicated[1].id})')

    @staticmethod
    def find_duplicated_parents():
        for duplicated in Family.get_duplicated_parents():
            print(f'Duplicated parent: {duplicated[0]} ({duplicated[0].id}) - {duplicated[1]} ({duplicated[1].id})')

    @staticmethod
    def find_duplicated_children():
        for duplicated in Family.get_duplicated_children():
            print(f'Duplicated child: {duplicated[0]} ({duplicated[0].id}) - {duplicated[1]} ({duplicated[1].id})')
