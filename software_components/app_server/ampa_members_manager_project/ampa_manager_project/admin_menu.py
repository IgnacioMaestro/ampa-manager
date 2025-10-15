from django.utils.translation import gettext_lazy as _

MENU = [
    {
        'group_label': _('Families'),
        'links': [
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'family',
                'label': _('Families'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'parent',
                'label': _('Parents'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'child',
                'label': _('Students'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'bankaccount',
                'label': _('Bank accounts'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'holder',
                'label': _('Holders'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'bankbiccode',
                'label': _('Códigos bancarios BIC'),
            },
        ]
    },
    {
        'group_label': _('After-schools'),
        'links': [
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'afterschool',
                'label': _('Actividades'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'afterschooledition',
                'label': _('Editions'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'afterschoolregistration',
                'label': _('Registrations'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'afterschoolreceipt',
                'label': _('Receipts'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'afterschoolremittance',
                'label': _('Remittances'),
            },
            {
                'type': 'view',
                'app': 'ampa_manager',
                'view': 'import_after_schools_activities',
                'label': _('Importar actividades'),
            },
            {
                'type': 'view',
                'app': 'ampa_manager',
                'view': 'import_after_schools_registrations',
                'label': _('Importar inscripciones'),
            },
        ]
    },
    {
        'group_label': _('Custody'),
        'links': [
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'custodyedition',
                'label': _('Editions'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'custodyregistration',
                'label': _('Registrations'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'custodyreceipt',
                'label': _('Receipts'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'custodyremittance',
                'label': _('Remittances'),
            },
            {
                'type': 'view',
                'app': 'ampa_manager',
                'view': 'import_custody',
                'label': _('Import asistencia'),
            },
        ]
    },
    {
        'group_label': _('Camps'),
        'links': [
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'campsedition',
                'label': _('Editions'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'campsregistration',
                'label': _('Registrations'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'campsreceipt',
                'label': _('Receipts'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'campsremittance',
                'label': _('Remittances'),
            },
            {
                'type': 'view',
                'app': 'ampa_manager',
                'view': 'import_camps',
                'label': _('Importar inscripciones'),
            },
        ]
    },
    {
        'group_label': _('Members'),
        'links': [
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'academiccourse',
                'label': _('Academic courses'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'activecourse',
                'label': _('Active course'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'membership',
                'label': _('Members'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'fee',
                'label': _('Fees'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'membershipreceipt',
                'label': _('Receipts'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'membershipremittance',
                'label': _('Remittances'),
            },
            {
                'type': 'view',
                'app': 'ampa_manager',
                'view': 'notify_members_campaign',
                'label': _('Members campaign'),
            },
        ]
    },
    {
        'group_label': _('Others'),
        'links': [
            {
                'type': 'model',
                'app': 'auth',
                'model': 'group',
                'label': _('Usuarios'),
            },
            {
                'type': 'model',
                'app': 'auth',
                'model': 'user',
                'label': _('Grupos'),
            },
            {
                'type': 'model',
                'app': 'ampa_manager',
                'model': 'dynamicsetting',
                'label': _('Settings'),
            },
        ]
    }
]