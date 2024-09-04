import datetime 
import json
import logging
import xml.etree.ElementTree as ET
from typing import Optional

from prpc_python import RpcApp

from sen_validator import sen_validator
from sen_validator.rules.ruleset_utils import get_year_ruleset

logger = logging.getLogger(__name__)
handler = logging.FileHandler(
    datetime.datetime.now().strftime("sen validator --%d-%m-%Y %H.%M.%S.log")
)

f_format = logging.Formatter("%(asctime)s - %(levelname)s - % (message)s")
handler.setFormatter(f_format)
logger.addHandler(handler)

app = RpcApp("validate_sen")

@app.call
def get_rules(ruleset: str) -> str:
    """
    param str ruleset: validation ruleset eg 0_0_1
    """
    ruleset_registry = get_year_ruleset(ruleset)

    rules = []
    for _, rule in ruleset_registry.items():
        rules.append(
            {
                "code": str(rule.code),
                "description": str(rule.code) + " - " + str(rule.message),
            }
        )

    return json.dumps(rules)

@app.call
def sen_validate(
    sen_data: dict,
    file_metadata: dict,
    selected_rules: Optional[list[str]] = None,
):
    """
    :param sen_data: eys are table names and values are SEN csv files.
    :param file_metadata: contains collection year and local authority as strings.
    :param selected_rules: array of rules the user has chosen. consists of rule codes as strings.

    :return issue_report: issue locations in the data.
    :return rule_defs: codes and descriptions of the rules that triggers issues in the data.
    """
    sen_data_file = sen_data["This year"][0]
    filetext = sen_data_file.read().decode("utf-8")
    # root = ET.fromstring(filetext)

    # # fulltree = ET.parse("fake_data\\fake_SEN_data.xml")
    # # root = fulltree.getroot()

    # raw_data = sen_validator.convert_data(root)

    # Send string-format data to the frontend.
    sen_data_tables = {
        table_name: table_df.to_json(orient="records")
        for table_name, table_df in raw_data.items()
    }

    # Convert date columns to datetime format to enable comparison in rules.
    data_files = sen_validator.process_data(raw_data)
    # get rules to run based on specified year.
    ruleset_registry = get_year_ruleset(file_metadata["collectionYear"])

    # run validation
    validator = sen_validator.SenValidator(data_files, ruleset_registry, selected_rules)

    # make return data json-serialisable

    # what the frontend will display
    issue_report = validator.full_issue_df.to_json(orient="records")
    multichild_issues = validator.multichild_issues.to_json(orient="records")

    # what the user will download
    user_report = validator.user_report.to_json(orient="records")

    validation_results = {
        "issue_locations": [issue_report],
        "multichild_issues": [multichild_issues],
        "data_tables": [sen_data_tables],
        "user_report": [user_report],
    }
    return validation_results