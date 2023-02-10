from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_manager.academic_course.admin import AcademicCourseAdmin
from ampa_manager.academic_course.admin import ActiveCourseAdmin
from ampa_manager.academic_course.models.academic_course import AcademicCourse
from ampa_manager.academic_course.models.active_course import ActiveCourse
from ampa_manager.activity.admin import ActivityPeriodAdmin, ActivityAdmin, AfterSchoolAdmin, \
    AfterSchoolEditionAdmin, AfterSchoolRegistrationAdmin
from ampa_manager.activity.models.activity import Activity
from ampa_manager.activity.models.activity_period import ActivityPeriod
from ampa_manager.activity.models.after_school.after_school import AfterSchool
from ampa_manager.activity.models.after_school.after_school_edition import AfterSchoolEdition
from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity_registration.admin import ActivityRegistrationAdmin
from ampa_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_manager.charge.admin_to_delete import ActivityRemittanceAdmin, ActivityReceiptAdmin
from ampa_manager.charge.admin.membership_admin import MembershipRemittanceAdmin, MembershipReceiptAdmin
from ampa_manager.charge.admin.after_school_admin import AfterSchoolReceiptAdmin, AfterSchoolRemittanceAdmin
from ampa_manager.charge.models.activity_receipt import ActivityReceipt
from ampa_manager.charge.models.activity_remittance import ActivityRemittance
from ampa_manager.charge.models.after_school_charge.after_school_receipt import AfterSchoolReceipt
from ampa_manager.charge.models.after_school_charge.after_school_remittance import AfterSchoolRemittance
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

admin.site.site_header = _('PTA Administration')
admin.site.site_title = _('PTA Administration')

# noinspection DuplicatedCode
admin.site.register(AcademicCourse, AcademicCourseAdmin)
admin.site.register(ActiveCourse, ActiveCourseAdmin)

admin.site.register(ActivityPeriod, ActivityPeriodAdmin)
admin.site.register(Activity, ActivityAdmin)

admin.site.register(AfterSchool, AfterSchoolAdmin)
admin.site.register(AfterSchoolEdition, AfterSchoolEditionAdmin)
admin.site.register(AfterSchoolRegistration, AfterSchoolRegistrationAdmin)

admin.site.register(Child, ChildAdmin)
admin.site.register(Parent, ParentAdmin)
# noinspection DuplicatedCode
admin.site.register(Family, FamilyAdmin)

# noinspection DuplicatedCode
admin.site.register(BankAccount, BankAccountAdmin)
admin.site.register(Holder, HolderAdmin)
admin.site.register(BankBicCode, BankBicCodeAdmin)
admin.site.register(Membership, MembershipAdmin)

admin.site.register(ActivityRegistration, ActivityRegistrationAdmin)
admin.site.register(ActivityRemittance, ActivityRemittanceAdmin)
admin.site.register(ActivityReceipt, ActivityReceiptAdmin)
admin.site.register(MembershipRemittance, MembershipRemittanceAdmin)
admin.site.register(MembershipReceipt, MembershipReceiptAdmin)
admin.site.register(Fee)
admin.site.register(AfterSchoolReceipt, AfterSchoolReceiptAdmin)
admin.site.register(AfterSchoolRemittance, AfterSchoolRemittanceAdmin)
