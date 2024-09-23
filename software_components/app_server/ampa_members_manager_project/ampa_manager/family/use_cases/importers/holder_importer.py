from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.parent import Parent


class HolderImporter:

    def __init__(self, parent: Parent, bank_account: BankAccount):
        self.result = ImportModelResult(Holder.__name__)
        self.parent = parent
        self.bank_account = bank_account
        self.holder = None

    def import_holder(self) -> ImportModelResult:
        if self.parent:
            if self.bank_account:
                self.holder = Holder.find(self.parent, self.bank_account)
                if self.holder:
                    self.result.set_not_modified(self.holder)
                else:
                    self.holder = Holder.objects.create_for_active_course(
                        parent=self.parent, bank_account=self.bank_account)
                    self.result.set_created(self.holder)
            else:
                self.result.set_error(_('Missing bank account'))
        else:
            self.result.set_error(_('Missing parent'))

        return self.result
