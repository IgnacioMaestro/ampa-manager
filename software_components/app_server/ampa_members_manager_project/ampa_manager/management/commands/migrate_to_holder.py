from django.core.management.base import BaseCommand

from ampa_manager.management.commands.to_holder_migrator.to_holder_migrator import ToHolderMigrator


class Command(BaseCommand):
    help = "Migration to Holder data model."

    def handle(self, *args, **options):
        ToHolderMigrator.migrate_after_school_registrations()
