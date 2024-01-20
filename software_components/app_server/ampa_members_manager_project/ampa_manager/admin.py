from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.admin import AcademicCourseAdmin
from ampa_manager.academic_course.admin import ActiveCourseAdmin
from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.admin.after_school_admin import AfterSchoolRegistrationAdmin, AfterSchoolEditionAdmin, \
    AfterSchoolAdmin
from ampa_manager.activity.admin.camps_admin import CampsEditionAdmin, CampsRegistrationAdmin
from ampa_manager.activity.admin.custody_admin import CustodyEditionAdmin, CustodyRegistrationAdmin
from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.camps.camps_edition import CampsEdition
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.models.custody.custody_edition import CustodyEdition
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.charge.admin.after_school_admin import AfterSchoolReceiptAdmin, AfterSchoolRemittanceAdmin
from ampa_manager.charge.admin.camps_admin import CampsReceiptAdmin, CampsRemittanceAdmin
from ampa_manager.charge.admin.custody_admin import CustodyReceiptAdmin, CustodyRemittanceAdmin
from ampa_manager.charge.admin.fee_admin import FeeAdmin
from ampa_manager.charge.admin.membership_admin import MembershipRemittanceAdmin, MembershipReceiptAdmin
from ampa_manager.charge.models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from ampa_manager.charge.models.after_school_charge.after_school_remittance import AfterSchoolRemittance
from ampa_manager.charge.models.camps.camps_receipt import CampsReceipt
from ampa_manager.charge.models.camps.camps_remittance import CampsRemittance
from ampa_manager.charge.models.custody.custody_receipt import CustodyReceipt
from ampa_manager.charge.models.custody.custody_remittance import CustodyRemittance
from ampa_manager.charge.models.fee.fee import Fee
from ampa_manager.charge.models.membership_receipt import MembershipReceipt
from ampa_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_manager.family.admin.bank_account_admin import BankAccountAdmin
from ampa_manager.family.admin.bank_bic_code_admin import BankBicCodeAdmin
from ampa_manager.family.admin.child_admin import ChildAdmin
from ampa_manager.family.admin.family_admin import FamilyAdmin
from ampa_manager.family.admin.holder_admin import HolderAdmin
from ampa_manager.family.admin.membership_admin import MembershipAdmin
from ampa_manager.family.admin.parent_admin import ParentAdmin
from ampa_manager.family.models.bank_account.bank_account import BankAccount
from ampa_manager.family.models.bank_account.bank_bic_code import BankBicCode
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.family.models.membership import Membership
from ampa_manager.family.models.parent import Parent
from ampa_manager.importation.admin.custody_importation_admin import CustodyImportationAdmin
from ampa_manager.importation.admin.custody_importation_row_admin import CustodyImportationRowAdmin
from ampa_manager.importation.models.custody_importation import CustodyImportation
from ampa_manager.importation.models.custody_importation_row import CustodyImportationRow

admin.site.site_header = _('PTA Administration')
admin.site.site_title = _('PTA Administration')

# noinspection DuplicatedCode
admin.site.register(AcademicCourse, AcademicCourseAdmin)
admin.site.register(ActiveCourse, ActiveCourseAdmin)

admin.site.register(AfterSchool, AfterSchoolAdmin)
admin.site.register(AfterSchoolEdition, AfterSchoolEditionAdmin)
admin.site.register(AfterSchoolRegistration, AfterSchoolRegistrationAdmin)

admin.site.register(CustodyEdition, CustodyEditionAdmin)
admin.site.register(CustodyRegistration, CustodyRegistrationAdmin)

admin.site.register(CampsEdition, CampsEditionAdmin)
admin.site.register(CampsRegistration, CampsRegistrationAdmin)

admin.site.register(Child, ChildAdmin)
# noinspection DuplicatedCode
admin.site.register(Parent, ParentAdmin)
admin.site.register(Family, FamilyAdmin)

# noinspection DuplicatedCode
admin.site.register(BankAccount, BankAccountAdmin)
admin.site.register(Holder, HolderAdmin)
admin.site.register(BankBicCode, BankBicCodeAdmin)
admin.site.register(Membership, MembershipAdmin)

admin.site.register(MembershipRemittance, MembershipRemittanceAdmin)
admin.site.register(MembershipReceipt, MembershipReceiptAdmin)
admin.site.register(Fee, FeeAdmin)
admin.site.register(AfterSchoolReceipt, AfterSchoolReceiptAdmin)
admin.site.register(AfterSchoolRemittance, AfterSchoolRemittanceAdmin)
admin.site.register(CustodyReceipt, CustodyReceiptAdmin)
admin.site.register(CustodyRemittance, CustodyRemittanceAdmin)
admin.site.register(CampsReceipt, CampsReceiptAdmin)
admin.site.register(CampsRemittance, CampsRemittanceAdmin)

admin.site.register(CustodyImportation, CustodyImportationAdmin)
admin.site.register(CustodyImportationRow, CustodyImportationRowAdmin)
