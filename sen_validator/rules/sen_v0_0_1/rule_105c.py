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
    code="105c",
    module=SENTable.List_1,
    message="Date updated EHC plan issued is in the future - Query",
    affected_fields=["Date updated EHC plan issued"],
)
def validate(
    data_container: Mapping[SENTable, pd.DataFrame], rule_context: RuleContext
):
    df = data_container[list_1]

    df["Date updated EHC plan issued"] = pd.to_datetime(
        df["Date updated EHC plan issued"], dayfirst=True, errors="coerce"
    )

    future_birth = df[df["Date updated EHC plan issued"] > pd.to_datetime("today")]

    error_indices = list(future_birth.index)

    rule_context.push_issue(
        table=list_1, field="Date updated EHC plan issued", row=error_indices
    )


def test_validate():
    child_identifiers = pd.DataFrame(
        {
            "Date updated EHC plan issued": [
                # These should pass
                "01/01/2020",
                "02/03/2024",
                pd.NA,
                "20/12/2030",  # future, fail
            ]
        }
    )

    result = run_rule(validate, {list_1: child_identifiers})

    issues = list(result.issues)

    assert len(issues) == 1

    assert issues == [
        IssueLocator(SENTable.List_1, "Date updated EHC plan issued", 3),
    ]

    assert result.definition.code == "105c"
    assert (
        result.definition.message
        == "Date updated EHC plan issued is in the future - Query"
    )