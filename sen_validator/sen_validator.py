import copy
from typing import Optional

import pandas as pd

from sen_validator.ingress import *

# from sen_validator.datastore import create_datastore


class SenValidator:
    """A class to contain the processes of SEN_Validation. Generates error reports as dataframes.

    :param any data_files: Data files for validation, either a DataContainerWrapper object, or a
        dictionary of DataFrames.
    :param dir ruleset: The directory containing the validation rules to be run according to the year in which they were published.
    """

    def __init__(
        self,
        data_files,
        # ruleset_registry,
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
        # self.ruleset_registry = ruleset_registry

        # save independent version of data to be used in report.
        raw_data = copy.deepcopy(self.data_files)
        dfs, metadata_extras = read_from_text(raw_files=data_files)

        # TODO run
        # self.create_issue_report_df(selected_rules)

        
    def validate(self, selected_rules: Optional[list[str]] = None):
        logger.info("Creating Data store...")
        
        # data_store = create_datastore(self.dfs, self.metadata)



