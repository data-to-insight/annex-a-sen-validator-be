from typing import Mapping

import pandas as pd

from sen_validator.rule_engine import (
    SENTable,
    IssueLocator,
    RuleContext,
    rule_definition,
)
from sen_validator.test_engine import run_rule

list_1 = SENTable.List_1


@rule_definition(
    code="106a",
    module=SENTable.List_1,
    message="Initial EHCP date is after Updated Date",
    affected_fields=["Date initial EHC plan issued", "Date updated EHC plan issued"],
)
def validate(
    data_container: Mapping[SENTable, pd.DataFrame], rule_context: RuleContext
):
    df = data_container[list_1]
    df.index.name = "ROW_ID"

    df["Date initial EHC plan issued"] = pd.to_datetime(
        df["Date initial EHC plan issued"], dayfirst=True, errors="coerce"
    )
    df["Date updated EHC plan issued"] = pd.to_datetime(
        df["Date updated EHC plan issued"], dayfirst=True, errors="coerce"
    )

    df = df[df["Date initial EHC plan issued"] > df["Date updated EHC plan issued"]]
    df_issues = df.reset_index()

    link_id = tuple(
        zip(
            df_issues["Unique ID"],
            df_issues["Date initial EHC plan issued"],
            df_issues["Date updated EHC plan issued"],
        )
    )
    df_issues["ERROR_ID"] = link_id
    df_issues = (
        df_issues.groupby("ERROR_ID", group_keys=False)["ROW_ID"]
        .apply(list)
        .reset_index()
    )
    print(df_issues)

    rule_context.push_type_1(
        table=list_1,
        columns=["Date initial EHC plan issued", "Date updated EHC plan issued"],
        row_df=df_issues,
    )


def test_validate():
    fake_list = pd.DataFrame(
        [
            {
                "Unique ID": 1,
                "Date initial EHC plan issued": "01/01/2000",
                "Date updated EHC plan issued": "02/01/2000",
            },
            {
                "Unique ID": 1,
                "Date initial EHC plan issued": "01/01/2030",
                "Date updated EHC plan issued": "02/01/2030",
            },
            {
                "Unique ID": 2,
                "Date initial EHC plan issued": "01/01/2030",
                "Date updated EHC plan issued": "02/01/2030",
            },
            {
                "Unique ID": 3,
                "Date initial EHC plan issued": "01/01/2000",
                "Date updated EHC plan issued": "29/12/1999",
            },
            {
                "Unique ID": 4,
                "Date initial EHC plan issued": "01/01/1999",
                "Date updated EHC plan issued": "02/01/2000",
            },
        ]
    )

    result = run_rule(validate, {list_1: fake_list})

    issues = result.type1_issues

    issue_table = issues.table
    assert issue_table == list_1

    issue_columns = issues.columns
    assert issue_columns == [
        "Date initial EHC plan issued",
        "Date updated EHC plan issued",
    ]

    issue_rows = issues.row_df

    assert len(issue_rows) == 1

    assert isinstance(issue_rows, pd.DataFrame)
    assert issue_rows.columns.to_list() == ["ERROR_ID", "ROW_ID"]

    expected_df = pd.DataFrame(
        [
            {
                "ERROR_ID": (
                    3,
                    pd.to_datetime("01/01/2000", dayfirst=True, errors="coerce"),
                    pd.to_datetime("29/12/1999", dayfirst=True, errors="coerce"),
                ),
                "ROW_ID": [3],
            }
        ]
    )

    assert issue_rows.equals(expected_df)

    assert result.definition.code == "106a"
    assert result.definition.message == "Initial EHCP date is after Updated Date"
