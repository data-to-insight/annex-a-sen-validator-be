from typing import Mapping

import pandas as pd

from sen_validator.rule_engine import (
    SENTable,
    IssueLocator,
    RuleContext,
    rule_definition,
)

list_1 = SENTable.List_1

from sen_validator.test_engine import run_rule


@rule_definition(
    code="102b",
    module=SENTable.List_1,
    message="Age is 26 or over - Error",
    affected_fields=["Date of birth"],
)
def validate(
    data_container: Mapping[SENTable, pd.DataFrame], rule_context: RuleContext
):
    df = data_container[list_1]

    df["Date of birth"] = pd.to_datetime(
        df["Date of birth"], dayfirst=True, errors="coerce"
    )

    over_26 = df["Date of birth"] + pd.DateOffset(years=26) < pd.to_datetime("today")

    aged_26_plus = df[over_26]

    error_indices = list(aged_26_plus.index)

    rule_context.push_issue(table=list_1, field="Date of birth", row=error_indices)


def test_validate():
    child_identifiers = pd.DataFrame(
        {
            "Date of birth": [
                # These should pass
                "01/01/2020",
                "02/03/2024",
                "27/08/1999",
                "26/08/1999",
                pd.NA,
                # These should fail
                "27/08/1998",
                "26/08/1998",
                "X845212818005",
            ]
        }
    )

    result = run_rule(validate, {list_1: child_identifiers})

    issues = list(result.issues)

    assert len(issues) == 2

    assert issues == [
        IssueLocator(SENTable.List_1, "Date of birth", 5),
        IssueLocator(SENTable.List_1, "Date of birth", 6),
    ]

    assert result.definition.code == "102b"
    assert result.definition.message == "Age is 26 or over - Error"
