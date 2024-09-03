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
    code="201c",
    module=SENTable.List_2,
    message="Missing personal information - Ethnicity",
    affected_fields=["Ethnicity"],
)
def validate(
    data_container: Mapping[SENTable, pd.DataFrame], rule_context: RuleContext
):
    df = data_container[list_2]

    errors = df[df["Ethnicity"].isna()]
    error_indices = list(errors.index)
    rule_context.push_issue(table=list_2, field="Ethnicity", row=error_indices)


def test_validate():
    fake_list = pd.DataFrame(
        {
            "Ethnicity": [
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

    result = run_rule(validate, {list_2: fake_list})

    issues = list(result.issues)

    assert len(issues) == 2

    assert issues == [
        IssueLocator(SENTable.List_2, "Ethnicity", 5),
        IssueLocator(SENTable.List_2, "Ethnicity", 6),
    ]

    assert result.definition.code == "201c"
    assert result.definition.message == "Missing personal information - Ethnicity"
