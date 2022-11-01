import traceback

from ampa_members_manager.management.commands.import_command.importer import Importer
from ampa_members_manager.family.models.child import Child

import ampa_members_manager.management.commands.members_excel_settings as xls_settings


class ChildImporter(Importer):

    def __init__(self, sheet):
        self.sheet = sheet