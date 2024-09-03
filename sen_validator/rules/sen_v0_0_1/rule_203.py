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
    code="203",
    module=SENTable.List_2,
    message="No disability status given",
    affected_fields=["Does the child or young person have a disability?"],
)
def validate(
    data_container: Mapping[SENTable, pd.DataFrame], rule_context: RuleContext
):
    df = data_container[list_2]

    error_df = df[df["Does the child or young person have a disability?"].isna()]

    error_indices = list(error_df.index)

    rule_context.push_issue(
        table=list_2,
        field="Does the child or young person have a disability?",
        row=error_indices,
    )


def test_validate():
    fake_list = pd.DataFrame(
        {
            "Does the child or young person have a disability?": [
                # These should pass
                "Yeah",
                "Yes",
                "No",
                "Yes",
                "hmm",
                # These should fail
                pd.NA,
                pd.NA,
                "Yes",
            ]
        }
    )

    result = run_rule(validate, {list_2: fake_list})

    issues = list(result.issues)

    assert len(issues) == 2

    assert issues == [
        IssueLocator(
            SENTable.List_2, "Does the child or young person have a disability?", 5
        ),
        IssueLocator(
            SENTable.List_2, "Does the child or young person have a disability?", 6
        ),
    ]

    assert result.definition.code == "203"
    assert result.definition.message == "No disability status given"
