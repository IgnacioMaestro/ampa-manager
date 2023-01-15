from ampa_manager.activity.use_cases.importers.registration_excel_row import RegistrationExcelRow
from ampa_manager.family.models.family import Family
from ampa_manager.management.commands.importers.import_model_result import ImportModelResult
from ampa_manager.utils.processing_state import ProcessingState
from ampa_manager.utils.logger import Logger


class ImportRowResult:

    def __init__(self, row_index):
        self.row_index = row_index
        self.fields = RegistrationExcelRow(None, None, None, None, None, None, None, None, None, None, None, None,
                                           None, None, None, None)
        self.partial_results = []

    @property
    def success(self):
        if len(self.partial_results) > 0:
            for result in self.partial_results:
                if not result.success:
                    return False
            return True
        return False

    @property
    def errors(self):
        errors = []
        for result in self.partial_results:
            if result.error:
                errors.append(result.error)
        return ', '.join(errors)

    def print(self, logger: Logger):
        summary = f'OK' if self.success else f'ERROR: {self.errors}'
        logger.log(f'Row {self.row_index + 1} -> {summary}')

        if len(self.partial_results) > 0:
            for result in self.partial_results:
                logger.log(f' - {result}')
            return True
        else:
            logger.log(f'-')

    def add_partial_result(self, partial_result: ImportModelResult):
        self.partial_results.append(partial_result)

    @staticmethod
    def get_variation(before, after):
        if before < after:
            return f'{after} (+{after-before})'
        elif before > after:
            return f'{after} (-{before-after})'
        else:
            return f'{after} (=)'

    @staticmethod
    def print_stats(logger, results, counters_before, counters_after):

        totals, errors, created_families, success_count, not_success_count = ImportRowResult.get_totals(results)

        logger.log(f'TOTAL: {len(results)}')
        logger.log(f'- Imported: {success_count}')
        logger.log(f'- Not imported: {not_success_count}')

        for class_name, class_totals in totals.items():
            variation = ImportRowResult.get_variation(counters_before[class_name], counters_after[class_name])
            logger.log(f'- {class_name}: {variation}')
            for state, state_count in class_totals.items():
                logger.log(f'- {state.name}: {state_count}')

        logger.log(f'ERRORS: {len(errors)}:')
        for row_index, error in errors.items():
            logger.log(f'- Row {row_index+1}: {error}')

        if len(created_families) > 0:
            logger.log(f'WARNING: {len(created_families)} families were created:')
            for row_index, family in created_families:
                logger.log(f'- {family}')

    @staticmethod
    def get_totals(results):
        totals = {}
        errors = {}
        created_families = {}
        success_count = 0
        not_success_count = 0

        for result in results:

            if result.success:
                success_count += 1
            else:
                not_success_count += 1

            if result.errors:
                errors[result.row_index] = result.errors

            for partial_result in result.partial_results:
                if partial_result.class_name not in totals:
                    totals[partial_result.class_name] = {}
                if partial_result.state:
                    if partial_result.state not in totals[partial_result.class_name]:
                        totals[partial_result.class_name][partial_result.state] = 0
                    totals[partial_result.class_name][partial_result.state] += 1
                if partial_result.state2:
                    if partial_result.state2 not in totals[partial_result.class_name]:
                        totals[partial_result.class_name][partial_result.state2] = 0
                    totals[partial_result.class_name][partial_result.state2] += 1

                if partial_result.class_name == Family.__name__ and partial_result.state == ProcessingState.CREATED:
                    created_families[result.row_index] = partial_result.imported_object

        return totals, errors, created_families, success_count, not_success_count
