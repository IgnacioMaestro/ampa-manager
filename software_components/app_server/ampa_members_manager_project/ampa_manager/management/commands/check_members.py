from django.core.management.base import BaseCommand

from ampa_manager.family.models.family import Family
from ampa_manager.family.models.membership import Membership


class Command(BaseCommand):
    help = 'Check if these children are members'

    CHILDREN = []

    def handle(self, *args, **options):

        count = 0
        for child_data in Command.CHILDREN:
            count += 1
            child_name = child_data[0]
            family_surnames = child_data[1]

            family, error = Family.find(family_surnames)
            member = 'no'
            warning = 'ok'

            if family:
                if Membership.is_member_family(family):
                    member = 'sí'
                else:
                    warning = 'existe pero no es socia'

                child = family.find_child(child_name)
                if not child:
                    warning = 'hijo/a no encontrado/a'
            else:
                warning = 'familia no encontrada'

            print(f'{count},{child_name},{family_surnames},{member},{warning}')
