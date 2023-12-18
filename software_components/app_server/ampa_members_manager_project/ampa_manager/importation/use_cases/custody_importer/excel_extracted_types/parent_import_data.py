class ParentImportData:
    def __init__(self, holder_name_and_surnames: str, phone_number: str, email: str):
        self.__holder_name_and_surnames: str = holder_name_and_surnames
        self.__phone_number: str = phone_number
        self.__email: str = email

    @property
    def holder_name_and_surnames(self) -> str:
        return self.__holder_name_and_surnames

    @property
    def phone_number(self) -> str:
        return self.__phone_number

    @property
    def email(self) -> str:
        return self.__email
