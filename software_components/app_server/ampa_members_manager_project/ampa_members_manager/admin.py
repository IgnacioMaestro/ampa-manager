from django.contrib import admin

from ampa_members_manager.academic_course.admin import AcademicCourseAdmin
from ampa_members_manager.academic_course.models.academic_course import AcademicCourse
from ampa_members_manager.academic_course.models.active_course import ActiveCourse
from ampa_members_manager.activity.admin import RepetitiveActivityAdmin, UniqueActivityAdmin, ActivityPayablePartAdmin
from ampa_members_manager.activity.models.repetitive_activity import RepetitiveActivity
from ampa_members_manager.activity.models.activity_payable_part import ActivityPayablePart
from ampa_members_manager.activity.models.unique_activity import UniqueActivity
from ampa_members_manager.activity_registration.admin import ActivityRegistrationAdmin
from ampa_members_manager.activity_registration.models.activity_registration import ActivityRegistration
from ampa_members_manager.charge.admin import ActivityRemittanceAdmin
from ampa_members_manager.charge.models.activity_receipt import ActivityReceipt
from ampa_members_manager.charge.models.activity_remittance import ActivityRemittance
from ampa_members_manager.family.admin import FamilyAdmin, ParentAdmin, ChildAdmin, BankAccountAdmin, \
    AuthorizationAdmin, MembershipAdmin
from ampa_members_manager.family.models.authorization import Authorization
from ampa_members_manager.family.models.bank_account import BankAccount
from ampa_members_manager.family.models.child import Child
from ampa_members_manager.family.models.family import Family
from ampa_members_manager.family.models.membership import Membership
from ampa_members_manager.family.models.parent import Parent

admin.site.register(AcademicCourse, AcademicCourseAdmin)
admin.site.register(ActiveCourse)

admin.site.register(RepetitiveActivity, RepetitiveActivityAdmin)
admin.site.register(UniqueActivity, UniqueActivityAdmin)
admin.site.register(ActivityPayablePart, ActivityPayablePartAdmin)

admin.site.register(Child, ChildAdmin)
admin.site.register(Parent, ParentAdmin)
admin.site.register(Family, FamilyAdmin)

admin.site.register(BankAccount, BankAccountAdmin)
admin.site.register(Authorization, AuthorizationAdmin)
admin.site.register(Membership, MembershipAdmin)

admin.site.register(ActivityRegistration, ActivityRegistrationAdmin)

admin.site.register(ActivityRemittance, ActivityRemittanceAdmin)
admin.site.register(ActivityReceipt)
