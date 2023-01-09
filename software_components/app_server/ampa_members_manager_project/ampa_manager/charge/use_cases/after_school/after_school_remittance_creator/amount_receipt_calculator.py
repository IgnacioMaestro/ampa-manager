from abc import ABC, abstractmethod

from ampa_manager.activity.models.after_school.after_school_registration import AfterSchoolRegistration


class AmountReceiptCalculator(ABC):
    @abstractmethod
    def calculate(self, after_school_registration: AfterSchoolRegistration) -> float:
        pass
