from django.db.models.query import QuerySet

from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.charge.models.custody.custody_remittance import CustodyRemittance
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.academic_course.models.active_course import ActiveCourse


class CustodyRegistrationQuerySet(QuerySet):

    def of_custody_remittance(self, custody_remittance: CustodyRemittance):
        return self.filter(custody_edition__custody_remittance=custody_remittance)

    def of_child(self, child: Child):
        return self.filter(child=child)

    def of_holder(self, holder: Holder):
        return self.filter(holder=holder)

    def of_edition(self, custody_edition: CustodyEdition):
        return self.filter(custody_edition=custody_edition)
    
    def members(self):
        return self.filter(child__family__membership__academic_course=ActiveCourse.load())

    def no_members(self):
        return self.exclude(child__family__membership__academic_course=ActiveCourse.load())
