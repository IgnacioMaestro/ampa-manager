from __future__ import annotations
from typing import List, Dict

from ampa_manager.activity.use_cases.importers.registration_excel_row import RegistrationExcelRow
from ampa_manager.family.models.family import Family
from ampa_manager.management.commands.importers.import_model_result import ImportModelResult
from ampa_manager.utils.processing_state import ProcessingState
from ampa_manager.utils.logger import Logger


class ImportRowResult:

    def __init__(self, row_index):
        self.row_index = row_index
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
        logger.log(f'\nRow {self.row_index + 1} -> {summary}')

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
    def print_stats(logger: Logger, results: List[ImportRowResult], counters_before: Dict, counters_after: Dict):

        totals_by_model, totals_by_status, errors, created_families, success_count, not_success_count = ImportRowResult.get_totals(results)

        logger.log(f'\n\nTOTAL: {len(results)}\n')
        logger.log(f'- Imported: {success_count}')
        logger.log(f'- Not imported: {not_success_count}')

        logger.log(f'\n\nERRORS: {len(errors)}\n')
        for row_index, error in errors.items():
            logger.log(f'- Row {row_index+1}: {error}')

        if len(created_families) > 0:
            logger.log(f'\n\nWARNING: {len(created_families)} families were created\n')
            for row_index, family in created_families.items():
                logger.log(f'- {family}')

        logger.log(f'\n\nRESULTS BY MODEL\n')
        for model_name, model_totals in totals_by_model.items():
            variation = ImportRowResult.get_variation(counters_before[model_name], counters_after[model_name])
            logger.log(f'- {model_name}: {variation}')
            for state, state_count in model_totals.items():
                logger.log(f'· · · {state.name}: {state_count}')

        logger.log(f'\n\nRESULTS BY STATUS\n')
        for state, state_totals in totals_by_status.items():
            logger.log(f'- {state.name}')
            for model_name, model_count in state_totals.items():
                logger.log(f'· · · {model_name}: {model_count}')

    @staticmethod
    def get_totals(results):
        totals_by_model = {}
        totals_by_status = {}
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
                totals_by_model = ImportRowResult.add_total_by_model(totals_by_model, partial_result.class_name, partial_result.state, partial_result.state2)
                totals_by_status = ImportRowResult.add_total_by_status(totals_by_status, partial_result.class_name, partial_result.state, partial_result.state2)

                if partial_result.class_name == Family.__name__ and partial_result.state == ProcessingState.CREATED:
                    created_families[result.row_index] = partial_result.imported_object

        return totals_by_model, totals_by_status, errors, created_families, success_count, not_success_count

    @staticmethod
    def add_total_by_model(totals_by_model, class_name, state, state2):
        if class_name not in totals_by_model:
            totals_by_model[class_name] = {}
        if state:
            if state not in totals_by_model[class_name]:
                totals_by_model[class_name][state] = 0
            totals_by_model[class_name][state] += 1
        if state2:
            if state2 not in totals_by_model[class_name]:
                totals_by_model[class_name][state2] = 0
            totals_by_model[class_name][state2] += 1

        return totals_by_model

    @staticmethod
    def add_total_by_status(totals_by_status, class_name, state, state2):
        if state:
            if state not in totals_by_status:
                totals_by_status[state] = {}
            if class_name not in totals_by_status[state]:
                totals_by_status[state][class_name] = 0
            totals_by_status[state][class_name] += 1

        if state2:
            if state2 not in totals_by_status:
                totals_by_status[state2] = {}
            if class_name not in totals_by_status[state2]:
                totals_by_status[state2][class_name] = 0
            totals_by_status[state2][class_name] += 1

        return totals_by_status
