from ampa_manager.family.models.family import Family


class FamilyEmailExporter:
    def __init__(self, families: list[Family], family_emails: bool = True, parents_emails: bool = False):
        self.families = families
        self.parents_emails = parents_emails

    def export_to_csv(self) -> str:
        emails = []
        family: Family
        for family in self.families:
            for email in family.get_emails(parents_emails=self.parents_emails, family_emails=True):
                if email and email not in emails:
                    emails.append(email)
        return ",".join(emails)
