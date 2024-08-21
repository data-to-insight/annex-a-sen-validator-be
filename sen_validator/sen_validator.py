import copy
from typing import Optional

import pandas as pd

from sen_validator.ingress import *
from sen_validator.datastore import create_datastore, _process_metadata
from sen_validator.rule_engine import SENTable, RuleDefinition, RuleContext

# from sen_validator.datastore import create_datastore


def enum_keys(dict_input: dict):
    """
    Convert keys of a dictionary to its corresponding CINTable format.
    :param dict dict_input: dictionary of dataframes of CIN data
    :return dict enumed_dict: same data content with keys replaced.
    """
    enumed_dict = {}
    for enum_key in SENTable:
        # if enum_key == CINTable.Header, then enum_key.name == Header
        enumed_dict[enum_key] = dict_input[str(enum_key.name)]
    return enumed_dict


class SenValidator:
    """A class to contain the processes of SEN_Validation. Generates error reports as dataframes.

    :param any data_files: Data files for validation, either a DataContainerWrapper object, or a
        dictionary of DataFrames.
    :param dir ruleset: The directory containing the validation rules to be run according to the year in which they were published.
    """

    def __init__(
        self,
        data_files,
        metadata: dict[str, str],
        ruleset_registry,
        selected_rules: Optional[list[str]] = None,
    ) -> None:
        """
        Initialises SenValidator class.

        Creates DataFrame containing error report, and allows selection of individual instances of error using ERROR_ID

        :param list ruleset: The list of rules used in an individual validation session.
            Refers to rules in particular subdirectories of the rules directory.
        :param any data_files: The data extracted from input XLSX for validation.
        :param str issue_id: Can be used to choose a particular instance of an error using ERROR_ID.
        :param list selected_rules: array of rule codes (as strings) selected by the user. Determines what rules should be run.
        :returns: DataFrame of error report which could be a filtered version if issue_id is input.
        :rtype: DataFrame
        """

        self.data_files = data_files
        self.ruleset_registry = ruleset_registry

        # save independent version of data to be used in report.
        raw_data = copy.deepcopy(self.data_files)
        dfs, metadata_extras = read_from_text(raw_files=data_files)
        self.dfs = dfs

        self.create_issue_report_df(selected_rules)

        # TODO run
        # self.create_issue_report_df(selected_rules)

    def get_rules_to_run(
        self, registry, selected_rules: Optional[list[str]] = None
    ) -> list[RuleDefinition]:
        """
        Filters rules to be run based on user's selection in the frontend.
        :param Registry-class registry: record of all existing rules in rule pack
        :param list selected_rules: array of rule codes as strings
        """
        if selected_rules:
            rules_to_run = [
                rule for _, rule in registry.items() if str(rule.code) in selected_rules
            ]
            return rules_to_run
        else:
            return registry.values()

    def create_issue_report_df(self, selected_rules: Optional[list[str]] = None):
        enum_data_files = enum_keys(self.dfs)
        self.issue_instances = pd.DataFrame()
        self.full_issue_df = pd.DataFrame(
            columns=[
                "tables_affected",
                "columns_affected",
                "ROW_ID",
                "ERROR_ID",
                "rule_code",
                "rule_description",
                "rule_type",
                "la_level",
                "LAchildID",
            ]
        )
        self.rules_passed: list[str] = []

        self.rules_broken: list[str] = []
        self.rule_messages: list[str] = []
        self.la_rules_broken: list[str] = []

        registry = self.ruleset_registry

        rules_to_run = self.get_rules_to_run(registry, selected_rules)
        for rule in rules_to_run:
            data_files = copy.deepcopy(enum_data_files)
            ctx = RuleContext(rule)
            try:
                rule.func(data_files, ctx)
            except Exception as e:
                print(f"Error with rule {rule.code}: {type(e).__name__}, {e}")
            self.process_issues(rule, ctx)
