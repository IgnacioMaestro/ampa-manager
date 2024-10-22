class ExcelColumnDefinition:

    def __init__(self, key: str, label: str, short_label: str, formatter: callable):
        self.key = key
        self.label = label
        self.short_label = short_label
        self.formatter = formatter
