from django.core.management.base import BaseCommand
from django.db.models import QuerySet

from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder


class Command(BaseCommand):
    help = 'Set default bank account for families with only 1 bank account'

    def handle(self, *args, **options):
        for family in Family.objects.without_default_holder():
            holders: QuerySet[Holder] = Holder.objects.of_family(family)
            if (holders.count()) == 1:
                family.default_holder = holders.first()
                family.save()
            else:
                print(f'Family {family}: not set. Accounts: {holders.count()}')
