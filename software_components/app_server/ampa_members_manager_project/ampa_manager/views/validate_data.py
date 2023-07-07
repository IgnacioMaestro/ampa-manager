from typing import List

from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration
from ampa_manager.activity.models.camps.camps_registration import CampsRegistration
from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.utils.excel.titled_list import TitledList
from ampa_manager.utils.string_utils import StringUtils


def validate_data(request):
    context = {
        'validations': [
            # get_families_with_same_children_names(),
            # get_families_without_default_holder(),
            get_families_with_other_family_holder(),
            get_custody_registration_with_wrong_holder(),
            get_camps_registration_with_wrong_holder(),
            get_after_school_registration_with_wrong_holder(),
            # get_families_with_same_surnames(),
            # get_families_with_more_than_2_parents(),
            # get_families_with_only_1_parent(),
        ],
    }
    return render(request, 'validate_families_data.html', context)


def get_families_with_more_than_2_parents() -> TitledList:
    start = timezone.now()
    families = []
    for family in Family.objects.with_more_than_two_parents():
        parents = TitledList(family.get_html_link())
        for parent in family.parents.all():
            parents.append_element(parent.get_html_link())
        families.append(parents)

    print(f'get_families_with_more_than_2_parents {timezone.now() - start}')
    return TitledList(_('Families with more than 2 parents') + f' ({len(families)})', sublists=families)

def get_families_with_only_1_parent() -> TitledList:
    start = timezone.now()
    families = []
    for family in Family.objects.with_number_of_parents(1):
        parents = TitledList(family.get_html_link())
        for parent in family.parents.all():
            parents.append_element(parent.get_html_link())
        families.append(parents)

    print(f'get_families_with_only_1_parent {timezone.now() - start}')
    return TitledList(_('Families with 1 only father') + f' ({len(families)})', sublists=families)

def get_families_without_default_holder() -> TitledList:
    start = timezone.now()
    families = []
    for family in Family.objects.without_default_holder():
        holders = TitledList(family.get_html_link())
        for holder in Holder.objects.of_family(family):
            holders.append_element(holder.get_html_link())
        families.append(holders)

    print(f'get_families_without_default_holder {timezone.now() - start}')
    return TitledList(_('Families without default holder') + f' ({len(families)})', sublists=families)

def get_families_with_other_family_holder() -> TitledList:
    start = timezone.now()
    families = []
    for family in Family.objects.exclude(default_holder=None):
        if not holder_and_family_match(family.default_holder, family):
            family_holder = TitledList(family.get_html_link())
            family_holder.append_element(family.default_holder.get_html_link())
            families.append(family_holder)

    print(f'get_families_with_other_family_holder {timezone.now() - start}')
    return TitledList(_('Families with wrong holder') + f' ({len(families)})', sublists=families)

def get_custody_registration_with_wrong_holder() -> TitledList:
    start = timezone.now()
    registrations = get_registration_with_wrong_holder(CustodyRegistration)
    print(f'get_custody_registration_with_wrong_holder {timezone.now() - start}')
    return TitledList(_('Custody registration with wrong holder') + f' ({len(registrations)})', sublists=registrations)

def get_camps_registration_with_wrong_holder() -> TitledList:
    start = timezone.now()
    registrations = get_registration_with_wrong_holder(CampsRegistration)
    print(f'get_custody_registration_with_wrong_holder {timezone.now() - start}')
    return TitledList(_('Camps registration with wrong holder') + f' ({len(registrations)})', sublists=registrations)

def get_after_school_registration_with_wrong_holder() -> TitledList:
    start = timezone.now()
    registrations = get_registration_with_wrong_holder(AfterSchoolRegistration)
    print(f'get_custody_registration_with_wrong_holder {timezone.now() - start}')
    return TitledList(_('After-school registration with wrong holder') + f' ({len(registrations)})', sublists=registrations)

def get_registration_with_wrong_holder(registration_class) -> List[TitledList]:
    registrations = []
    for registration in registration_class.objects.all():
        if not holder_and_family_match(registration.holder, registration.child.family):
            registration_element = TitledList(registration.get_html_link())
            registration_element.append_element(_('Family') + ': ' + registration.child.family.get_html_link(print_id=True))
            registration_element.append_element(_('Child') + ': ' + registration.child.get_html_link())
            registration_element.append_element(_('Holder') + ': ' + registration.holder.get_html_link(print_family_id=True))
            registrations.append(registration_element)

    return registrations

def holder_and_family_match(holder, family):
    return family.parents.all().filter(id=holder.parent.id).exists()

def get_families_with_same_surnames() -> TitledList:
    start = timezone.now()
    processed_ids = []
    same_surnames = []
    for family1 in Family.objects.all():
        processed_ids.append(family1.id)

        surname = None
        for family2 in Family.objects.exclude(id__in=processed_ids):
            if StringUtils.compare_ignoring_everything(family1.surnames, family2.surnames):
                processed_ids.append(family2.id)
                if surname is None:
                    surname = TitledList(family1.surnames)
                    surname.append_element(family1.get_html_link(True, True))
                surname.append_element(family2.get_html_link(True, True))

        if surname is not None:
            same_surnames.append(surname)

    print(f'get_families_with_same_surnames {timezone.now() - start}')
    return TitledList(_('Families with same surnames') + f' ({len(same_surnames)})', sublists=same_surnames)

def get_families_with_same_children_names() -> TitledList:
    start = timezone.now()
    processed_ids = []
    same_children = []
    for family1 in Family.objects.all():
        processed_ids.append(family1.id)

        family1_child_csv = StringUtils.normalize(family1.get_children_names_csv())
        child_csv = None
        for family2 in Family.objects.exclude(id__in=processed_ids):
            if family1_child_csv == StringUtils.normalize(family2.get_children_names_csv()):
                processed_ids.append(family2.id)
                if child_csv is None:
                    child_csv = TitledList(family1_child_csv)
                    child_csv.append_element(family1.get_html_link(True, True))
                child_csv.append_element(family2.get_html_link(True, True))

        if child_csv is not None:
            same_children.append(child_csv)

    print(f'get_families_with_same_children_names {timezone.now()-start}')
    return TitledList(_('Families with same children names') + f' ({len(same_children)})', sublists=same_children)
