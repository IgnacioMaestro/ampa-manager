class ChildImportedFields:

    def __init__(self, name, year_of_birth, level):
        self.name = name
        self.year_of_birth = year_of_birth
        self.level = level

    def get_list(self):
        return [self.name, self.year_of_birth, self.level]