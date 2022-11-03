from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ampa_members_manager.academic_course.admin import AcademicCourseAdmin
from ampa_members_manager.academic_course.admin import ActiveCourseAdmin
from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.activity.admin import ActivityPeriodAdmin, ActivityAdmin
from ampa_members_manager.activity.models.activity import Activity
from ampa_members_manager.activity.models.activity_period import ActivityPeriod
from ampa_members_manager.activity_registration.admin import ActivityRegistrationAdmin
from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_members_manager.charge.admin import ActivityRemittanceAdmin, ActivityReceiptAdmin, MembershipRemittanceAdmin, MembershipReceiptAdmin
from ampa_members_manager.charge.models.activity_receipt import ActivityReceipt
from ampa_members_manager.charge.models.activity_remittance import ActivityRemittance
from ampa_members_manager.charge.models.membership_receipt import MembershipReceipt
from ampa_members_manager.charge.models.membership_remittance import MembershipRemittance
from ampa_members_manager.family.admin import FamilyAdmin, ParentAdmin, ChildAdmin, BankAccountAdmin, \
    AuthorizationAdmin, MembershipAdmin
from ampa_members_manager.family.models.authorization.authorization import Authorization
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.membership import Membership
from ampa_members_manager.family.models.parent import Parent

admin.site.site_header = _('PTA Administration')
admin.site.site_title = _('PTA Administration')

admin.site.register(AcademicCourse, AcademicCourseAdmin)
admin.site.register(ActiveCourse, ActiveCourseAdmin)

admin.site.register(ActivityPeriod, ActivityPeriodAdmin)
admin.site.register(Activity, ActivityAdmin)

admin.site.register(Child, ChildAdmin)
admin.site.register(Parent, ParentAdmin)
admin.site.register(Family, FamilyAdmin)

admin.site.register(BankAccount, BankAccountAdmin)
admin.site.register(Authorization, AuthorizationAdmin)
admin.site.register(Membership, MembershipAdmin)

admin.site.register(ActivityRegistration, ActivityRegistrationAdmin)
admin.site.register(ActivityRemittance, ActivityRemittanceAdmin)
admin.site.register(ActivityReceipt, ActivityReceiptAdmin)
admin.site.register(MembershipRemittance, MembershipRemittanceAdmin)
admin.site.register(MembershipReceipt, MembershipReceiptAdmin)
