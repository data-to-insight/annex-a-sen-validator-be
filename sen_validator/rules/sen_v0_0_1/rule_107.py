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
    code="107",
    module=SENTable.List_1,
    message="Child aged 6+ without either a) UPN, b) ULN",
    affected_fields=["Date of birth", "UPN", "ULN"],
)
def validate(
    data_container: Mapping[SENTable, pd.DataFrame], rule_context: RuleContext
):
    df = data_container[list_1]
    df.index.name = "ROW_ID"

    df["Date of birth"] = pd.to_datetime(
        df["Date of birth"], dayfirst=True, errors="coerce"
    )

    over_6 = df["Date of birth"] + pd.DateOffset(years=6) < pd.to_datetime("today")

    no_upn_uln = df["UPN"].isna() & df["ULN"].isna()

    df_issues = df[over_6 & no_upn_uln]

    df_issues = df_issues.reset_index()
    
    link_id = tuple(
        zip(
            df_issues["Unique ID"],
            df_issues["UPN"],
            df_issues["ULN"],
        )
    )
    df_issues["ERROR_ID"] = link_id
    df_issues = (
        df_issues.groupby("ERROR_ID", group_keys=False)["ROW_ID"]
        .apply(list)
        .reset_index()
    )
    

    rule_context.push_type_1(
        table=list_1,
        columns=["UPN", "ULN"],
        row_df=df_issues,
    )



def test_validate():
    fake_list = pd.DataFrame(
        [
            {
                "Unique ID": 1,
                "Date of birth":"27/08/2025",
                "UPN": "2",
                "ULN": pd.NA,
            },
            {
                "Unique ID": 1,
                "Date of birth":"27/08/2000",
                "UPN": pd.NA,
                "ULN": "1",
            },
            {
                "Unique ID": 2,
                "Date of birth":"27/08/2000",
                "UPN": "2",
                "ULN": pd.NA,
            },
            {
                "Unique ID": 3,
                "Date of birth":"27/08/2000",
                "UPN": pd.NA,
                "ULN":pd.NA,
            },
            {
                "Unique ID": 6,
                "Date of birth":"27/08/2025",
                "UPN": pd.NA,
                "ULN":pd.NA,
            },
            {
                "Unique ID": 4,
                "Date of birth":"27/08/2015",
                "UPN": "2",
                "ULN": "1",
            },
        ]
    )

    result = run_rule(validate, {list_1: fake_list})

    issues = result.type1_issues

    issue_table = issues.table
    assert issue_table == list_1

    issue_columns = issues.columns
    assert issue_columns == [
        "UPN",
        "ULN",
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
                    pd.NA,
                    pd.NA,
                ),
                "ROW_ID": [3],
            }
        ]
    )

    assert issue_rows.equals(expected_df)

    assert result.definition.code == "107"
    assert (
        result.definition.message
        == "Child aged 6+ without either a) UPN, b) ULN"
    )

