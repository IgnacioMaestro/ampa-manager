from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe

from ampa_manager.family.models.family import Family
from ampa_manager.family.models.holder.holder import Holder
from ampa_manager.utils.excel.titled_list import TitledList
from ampa_manager.utils.string_utils import StringUtils


def validate_families_data(request):
    context = {
        'families_with_same_number_and_name_children': get_families_with_same_number_and_name_children(),
        'families_without_default_holder': get_families_families_without_default_holder(),
        'families_with_same_surnames': get_families_with_same_surnames(),
        'families_with_more_than_2_parents': get_families_with_more_than_2_parents(),
        'families_with_only_1_parent': get_families_with_only_1_parent(),
    }
    return render(request, 'validate_families_data.html', context)

def get_families_with_more_than_2_parents() -> TitledList:
    families = TitledList('Familias con mas de 2 padres')
    for family in Family.objects.with_more_than_two_parents():
        parents = TitledList(get_family_link(family))
        for parent in family.parents.all():
            parents.append_element(get_parent_link(parent))
        families.append_sublist(parents)
    return families

def get_families_with_only_1_parent() -> TitledList:
    families = TitledList('Familias con 1 sólo padre')
    for family in Family.objects.with_number_of_parents(1):
        parents = TitledList(get_family_link(family))
        for parent in family.parents.all():
            parents.append_element(get_parent_link(parent))
        families.append_sublist(parents)
    return families

def get_families_families_without_default_holder() -> TitledList:
    families = TitledList('Familias sin titular por defecto')
    for family in Family.objects.without_default_holder():
        holders = TitledList(get_family_link(family))
        for holder in Holder.objects.of_family(family):
            holders.append_element(get_holder_link(holder))
        families.append_sublist(holders)
    return families

def get_families_with_same_surnames() -> TitledList:
    processed_ids = []
    surnames = TitledList('Familias con apellidos repetidos')
    for family1 in Family.objects.all():
        surname = None
        processed_ids.append(family1.id)
        for family2 in Family.objects.exclude(id__in=processed_ids):
            if StringUtils.compare_ignoring_everything(family1.surnames, family2.surnames):
                if surname is None:
                    surname = TitledList(family1.surnames)
                    surname.append_element(get_family_link(family1, True, True))
                surname.append_element(get_family_link(family2, True, True))

        if surname is not None:
            surnames.append_sublist(surname)

    return surnames

def get_families_with_same_number_and_name_children() -> TitledList:
    processed_ids = []
    processed_child_csv = []
    children = TitledList('Familias con el mismo nº de hijos y nombres')
    for family1 in Family.objects.all():
        processed_ids.append(family1.id)

        family1_child_csv = StringUtils.normalize(get_family_children_csv(family1))

        if family1_child_csv in processed_child_csv:
            continue

        processed_child_csv.append(family1_child_csv)

        child_csv = None

        for family2 in Family.objects.exclude(id__in=processed_ids):
            family2_child_csv = StringUtils.normalize(get_family_children_csv(family2))

            if family1_child_csv == family2_child_csv:
                if child_csv is None:
                    child_csv = TitledList(family1_child_csv)
                    child_csv.append_element(get_family_link(family1, True, True))
                child_csv.append_element(get_family_link(family2, True, True))

        if child_csv is not None:
            children.append_sublist(child_csv)

    return children

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

def get_model_link(model_name: str, model_id: int, link_text) -> str:
    app_label = 'ampa_manager'
    model_name = model_name
    link_url = reverse('admin:%s_%s_change' % (app_label, model_name), args=[model_id])
    return mark_safe(f'<a href="{link_url}">{link_text}</a>')
