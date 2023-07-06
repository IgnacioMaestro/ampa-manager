from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from ampa_manager.activity.models.custody.custody_registration import CustodyRegistration
from ampa_manager.family.models.child import Child
from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.utils.excel.titled_list import TitledList
from ampa_manager.utils.string_utils import StringUtils


def validate_families_data(request):
    context = {
        'validations': [
            # get_families_with_same_children_names(),
            # get_families_without_default_holder(),
            # get_families_with_other_family_holder(),
            get_custody_registration_with_wrong_holder(),
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
        parents = TitledList(get_family_link(family))
        for parent in family.parents.all():
            parents.append_element(get_parent_link(parent))
        families.append(parents)

    print(f'get_families_with_more_than_2_parents {timezone.now() - start}')
    return TitledList(_('Families with more than 2 parents') + f' ({len(families)})', sublists=families)

def get_families_with_only_1_parent() -> TitledList:
    start = timezone.now()
    families = []
    for family in Family.objects.with_number_of_parents(1):
        parents = TitledList(get_family_link(family))
        for parent in family.parents.all():
            parents.append_element(get_parent_link(parent))
        families.append(parents)

    print(f'get_families_with_only_1_parent {timezone.now() - start}')
    return TitledList(_('Families with 1 only father') + f' ({len(families)})', sublists=families)

def get_families_without_default_holder() -> TitledList:
    start = timezone.now()
    families = []
    for family in Family.objects.without_default_holder():
        holders = TitledList(get_family_link(family))
        for holder in Holder.objects.of_family(family):
            holders.append_element(get_holder_link(holder))
        families.append(holders)

    print(f'get_families_without_default_holder {timezone.now() - start}')
    return TitledList(_('Families without default holder') + f' ({len(families)})', sublists=families)

def get_families_with_other_family_holder() -> TitledList:
    start = timezone.now()
    families = []
    for family in Family.objects.exclude(default_holder=None):
        if not holder_and_family_match(family.default_holder, family):
            family_holder = TitledList(get_family_link(family))
            family_holder.append_element(get_holder_link(family.default_holder))
            families.append(family_holder)

    print(f'get_families_with_other_family_holder {timezone.now() - start}')
    return TitledList(_('Families with other family holder') + f' ({len(families)})', sublists=families)

def get_custody_registration_with_wrong_holder() -> TitledList:
    start = timezone.now()
    registrations = []
    for registration in CustodyRegistration.objects.all():
        if not holder_and_family_match(registration.holder, registration.child.family):
            registration_element = TitledList(get_custody_registration_link(registration))
            registration_element.append_element(get_family_link(registration.child.family))
            registration_element.append_element(get_child_link(registration.child))
            registration_element.append_element(get_holder_link(registration.holder))
            registrations.append(registration_element)

    print(f'get_custody_registration_with_wrong_holder {timezone.now() - start}')
    return TitledList(_('Custody registration with wrong holder') + f' ({len(registrations)})', sublists=registrations)

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
                    surname.append_element(get_family_link(family1, True, True))
                surname.append_element(get_family_link(family2, True, True))

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

        family1_child_csv = StringUtils.normalize(get_family_children_csv(family1))
        child_csv = None
        for family2 in Family.objects.exclude(id__in=processed_ids):
            if family1_child_csv == StringUtils.normalize(get_family_children_csv(family2)):
                processed_ids.append(family2.id)
                if child_csv is None:
                    child_csv = TitledList(family1_child_csv)
                    child_csv.append_element(get_family_link(family1, True, True))
                child_csv.append_element(get_family_link(family2, True, True))

        if child_csv is not None:
            same_children.append(child_csv)

    print(f'get_families_with_same_children_names {timezone.now()-start}')
    return TitledList(_('Families with same children names') + f' ({len(same_children)})', sublists=same_children)

def get_family_children_csv(family):
    return ', '.join([c.name for c in family.child_set.all()])

def get_holder_link(holder) -> str:
    return get_model_link('holder', holder.id, str(holder))

def get_family_link(family, print_parents=False, print_children=False) -> str:
    link_text = str(family)
    if print_parents:
        parents_names = [p.full_name for p in family.parents.all()]
        link_text += '. <b>Padres</b>: ' + ', '.join(parents_names)
    if print_children:
        children_names = [c.name for c in family.child_set.all()]
        link_text += '. <b>Hijos</b>: ' + ', '.join(children_names)

    return get_model_link('family', family.id, link_text)

def get_parent_link(parent) -> str:
    return get_model_link('parent', parent.id, str(parent))

def get_child_link(parent) -> str:
    return get_model_link(Child.__name__.lower(), parent.id, str(parent))

def get_custody_registration_link(registration) -> str:
    return get_model_link(CustodyRegistration.__name__.lower(), registration.id, str(registration))

def get_model_link(model_name: str, model_id: int, link_text) -> str:
    app_label = 'ampa_manager'
    model_name = model_name
    link_url = reverse('admin:%s_%s_change' % (app_label, model_name), args=[model_id])
    return mark_safe(f'<a href="{link_url}">{link_text}</a>')
