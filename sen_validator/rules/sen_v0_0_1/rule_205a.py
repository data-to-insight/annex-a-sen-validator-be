from typing import Mapping

import pandas as pd

from sen_validator.rule_engine import (
    SENTable,
    IssueLocator,
    RuleContext,
    rule_definition,
)

list_2 = SENTable.List_2

from sen_validator.test_engine import run_rule


@rule_definition(
    code="205a",
    module=SENTable.List_2,
    message="Date of birth is in the future - Query",
    affected_fields=["Date of birth"],
)
def validate(
    data_container: Mapping[SENTable, pd.DataFrame], rule_context: RuleContext
):
    df = data_container[list_2]

    df["Date of birth"] = pd.to_datetime(
        df["Date of birth"], dayfirst=True, errors="coerce"
    )

    future_birth = df[df["Date of birth"] > pd.to_datetime("today")]

    error_indices = list(future_birth.index)

    rule_context.push_issue(table=list_2, field="Date of birth", row=error_indices)


def test_validate():
    fake_list = pd.DataFrame(
        {
            "Date of birth": [
                # These should pass
                "01/01/2020",
                "02/03/2024",
                pd.NA,
                "20/12/2030",  # future, fail
            ]
        }
    )

    result = run_rule(validate, {list_2: fake_list})

    issues = list(result.issues)

    assert len(issues) == 1

    assert issues == [
        IssueLocator(SENTable.List_2, "Date of birth", 3),
    ]

    assert result.definition.code == "205a"
    assert result.definition.message == "Date of birth is in the future - Query"
