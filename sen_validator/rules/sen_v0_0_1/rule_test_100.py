from typing import Mapping

import pandas as pd

from sen_validator.rule_engine import (
    SENTable,
    IssueLocator,
    RuleContext,
    rule_definition,
)

list_1 = SENTable.List_1

# from sen_validator.test_engine import run_rule


@rule_definition(
    code="test_1",
    module=SENTable.List_1,
    message="Test rule 1",
    affected_fields=["Unique ID"],
)
def validate(
    data_container: Mapping[SENTable, pd.DataFrame], rule_context: RuleContext
):
    df = data_container[list_1]

    errors = df[df["Unique ID"].notna()]
    error_indices = list(errors.index)
    rule_context.push_issue(table=list_1, field="Unique ID", row=error_indices)
