class ParentImportedFields:

    def __init__(self, name_and_surnames, phone_number, additional_phone_number, email):
        self.name_and_surnames = name_and_surnames
        self.phone_number = phone_number
        self.additional_phone_number = additional_phone_number
        self.email = email

    def get_list(self):
        return [self.name_and_surnames, self.phone_number, self.additional_phone_number, self.email]
