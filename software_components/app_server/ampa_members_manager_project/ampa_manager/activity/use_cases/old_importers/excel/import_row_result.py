from __future__ import annotations
from typing import List, Dict

from ampa_manager.activity.use_cases.importers.import_model_result import ImportModelResult
from ampa_manager.activity.use_cases.old_importers.excel.excel_row import ExcelRow
from ampa_manager.activity.use_cases.old_importers.excel.titled_list import TitledList
from ampa_manager.family.models.family import Family
from ampa_manager.utils.processing_state import ProcessingState
from ampa_manager.utils.logger import Logger


class ImportRowResult:

    def __init__(self, row: ExcelRow):
        self.row = row
        self.partial_results = []
        self.error = None

    @property
    def success(self):
        if self.error is None and len(self.partial_results) > 0:
            for result in self.partial_results:
                if not result.success:
                    return False
            return True
        return False

    @property
    def errors(self):
        errors = []

        if self.error is not None:
            errors.append(self.error)

        for result in self.partial_results:
            if result.error:
                errors.append(f'{result.class_name}: {result.error}')

        return ', '.join(errors)

    @property
    def warnings(self):
        warnings = []

        for result in self.partial_results:
            if len(result.warnings) > 0:
                warnings.extend(result.warnings)

        return ', '.join(str(w) for w in warnings)

    def __str__(self):
        summary = 'OK' if self.success else f'ERROR: {self.errors}'
        description = f'\nRow {self.row.number} -> {summary}'

        if len(self.partial_results) > 0:
            for result in self.partial_results:
                description += f' - {result}'
        else:
            description += f' -'

        return description

    def as_titled_list(self) -> TitledList:
        row_status = 'OK' if self.success else f'ERROR: {self.errors}'
        details = TitledList(f'\nRow {self.row.number} -> {row_status}')
        for result in self.partial_results:
            details.append_element(str(result))
        return details

    def add_partial_result(self, partial_result: ImportModelResult):
        self.partial_results.append(partial_result)

    def add_partial_results(self, partial_results: List[ImportModelResult]):
        for partial_result in partial_results:
            self.add_partial_result(partial_result)

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

        totals_by_model, totals_by_status, errors, warnings, created_families, success_count, not_success_count = \
            ImportRowResult.get_totals(results)

        logger.log('\n\nTOTAL:')
        logger.log(f'- Rows imported successfully: {success_count}/{len(results)}')
        logger.log(f'- Rows not imported: {not_success_count}/{len(results)}')

        logger.log(f'\n\nERRORS: {len(errors)}')
        for row_index, error in errors.items():
            logger.log(f'- Row {row_index+1}: {error}')

        logger.log(f'\n\nWARNINGS:')
        if len(created_families) > 0:
            logger.log(f'- {len(created_families)} families were created')
            for row_index, family in created_families.items():
                logger.log(f'--- {family}')
        for row_index, warning in warnings.items():
            logger.log(f'- Row {row_index + 1}: {warning}')

        logger.log(f'\n\nRESULTS BY MODEL\n')
        for model_name, model_totals in totals_by_model.items():
            variation = ImportRowResult.get_variation(counters_before[model_name], counters_after[model_name])
            logger.log(f'- {model_name}: {variation}')
            for state, state_count in model_totals.items():
                logger.log(f'--- {state.name}: {state_count}')

        logger.log(f'\n\nRESULTS BY STATUS\n')
        for state, state_totals in totals_by_status.items():
            logger.log(f'- {state.name}')
            for model_name, model_count in state_totals.items():
                logger.log(f'--- {model_name}: {model_count}')

    @staticmethod
    def get_totals(results: List[ImportRowResult]):
        totals_by_model = {}
        totals_by_status = {}
        errors = {}
        warnings = {}
        created_families = {}
        success_count = 0
        not_success_count = 0

        for result in results:

            if result.success:
                success_count += 1
            else:
                not_success_count += 1

            if result.errors:
                errors[result.row.index] = result.errors

            if result.warnings:
                warnings[result.row.index] = result.warnings

            for partial_result in result.partial_results:
                totals_by_model = ImportRowResult.add_total_by_model(totals_by_model, partial_result.class_name, partial_result.state, partial_result.state2)
                totals_by_status = ImportRowResult.add_total_by_status(totals_by_status, partial_result.class_name, partial_result.state, partial_result.state2)

                if partial_result.class_name == Family.__name__ and partial_result.state == ProcessingState.CREATED:
                    created_families[result.row.index] = partial_result.imported_object

        return totals_by_model, totals_by_status, errors, warnings, created_families, success_count, not_success_count

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
