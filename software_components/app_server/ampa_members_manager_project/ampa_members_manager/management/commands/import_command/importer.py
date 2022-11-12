import re
from datetime import datetime

from ampa_members_manager.management.commands.import_command.surnames import SURNAMES


class Importer:
    STATUS_NOT_PROCESSED = 'not_processed'
    STATUS_CREATED = 'created'
    STATUS_UPDATED = 'updated'
    STATUS_ADDED_TO_FAMILY = 'added_to_family'
    STATUS_SET_AS_DEFAULT = 'set_as_default'
    STATUS_NOT_MODIFIED = 'not_modified'

    @staticmethod
    def parse_bool(str_bool):
        if str_bool:
            return str_bool.strip().lower() in ["si", "sí", "yes", "1", "true"]
        else:
            return False
    
    @staticmethod
    def clean_email(str_value):
        return Importer.clean_string_value(str_value, lower=True)
    
    @staticmethod
    def clean_surname(str_value):
        str_value = Importer.clean_string_value(str_value, title=True)
        if str_value is not None:
            for wrong, right in SURNAMES.items():
                if wrong in str_value:
                    str_value = str_value.replace(wrong, right)
            return str_value
        return None

    @staticmethod
    def clean_string_value(str_value, lower=False, title=False):
        if str_value is not None:
            clean_value = Importer.remove_duplicate_spaces(str_value).strip()
            if clean_value not in [' ', '']:
                if lower:
                    clean_value = clean_value.lower()
                if title:
                    clean_value = clean_value.title()
                return clean_value
        return None
    
    @staticmethod
    def clean_iban(str_value):
        if str_value is not None:
            return Importer.remove_spaces(str_value).strip().upper()
        return None
    
    @staticmethod
    def clean_date(str_value, format='%d/%m/%y'):
        if str_value not in [None, '']:
            return datetime.strptime(Importer.remove_spaces(str_value), format)
        return None
    
    @staticmethod
    def clean_integer(str_value, lower=False, title=False):
        if str_value not in [None, '']:
            clean_value = Importer.remove_spaces(str_value).strip()
            return int(float(clean_value))
        return None
    
    @staticmethod
    def remove_duplicate_spaces(str_value):
        if str_value is not None:
            return re.sub(' +', ' ', str(str_value))
        return None
    
    @staticmethod
    def remove_spaces(str_value):
        if str_value is not None:
            return str(str_value).replace(' ', '')
        return None
    
    @staticmethod
    def clean_phone(phone):
        phone = Importer.clean_string_value(phone)
        if phone and str(phone) not in ['0', '0.0', '0,0']:
            phone = str(phone)
            if not phone.startswith('+34'):
                phone = f'+34{phone}'
            if phone.endswith('.0'):
                phone = phone[:-2]
            if phone.endswith(',0'):
                phone = phone[:-2]
            return phone
        else:
            return ''
