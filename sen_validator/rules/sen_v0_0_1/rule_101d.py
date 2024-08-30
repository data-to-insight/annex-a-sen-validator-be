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
    code="101d",
    module=SENTable.List_1,
    message="Missing personal information - SEN primary need",
    affected_fields=["SEN primary need"],
)
def validate(
    data_container: Mapping[SENTable, pd.DataFrame], rule_context: RuleContext
):
    df = data_container[list_1]

    errors = df[df["SEN primary need"].isna()]
    error_indices = list(errors.index)
    rule_context.push_issue(table=list_1, field="SEN primary need", row=error_indices)


def test_validate():
    fake_list = pd.DataFrame(
        {
            "SEN primary need": [
                # These should pass
                "A950000178301",
                "05/12/1993",
                "05/12/1993",
                "ASFFAGSVSV123",
                "R325",
                # These should fail
                pd.NA,
                pd.NA,
                "X845212818005",
            ]
        }
    )

    result = run_rule(validate, {list_1: fake_list})

    issues = list(result.issues)

    assert len(issues) == 2

    assert issues == [
        IssueLocator(SENTable.List_1, "SEN primary need", 5),
        IssueLocator(SENTable.List_1, "SEN primary need", 6),
    ]

    assert result.definition.code == "101d"
    assert (
        result.definition.message == "Missing personal information - SEN primary need"
    )
