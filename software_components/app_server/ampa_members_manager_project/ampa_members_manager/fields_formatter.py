class FieldsFormatter:
    @classmethod
    def clean_name(cls, name: str) -> str:
        return cls.capitalize_and_delete_spaces(name)

    @classmethod
    def capitalize_and_delete_spaces(cls, name: str) -> str:
        return name.title().strip()
