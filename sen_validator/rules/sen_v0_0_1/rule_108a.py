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
    code="108a",
    module=SENTable.List_1,
    message="School aged child/young person (5-16) without  main OR subsidiary education establishment",
    affected_fields=[
        "Date of birth",
        "Main education establishment – URN",
        "Subsidiary education establishment – phase (dual registration)",
    ],
)
def validate(
    data_container: Mapping[SENTable, pd.DataFrame], rule_context: RuleContext
):
    df = data_container[list_1]
    df.index.name = "ROW_ID"

    df["Date of birth"] = pd.to_datetime(
        df["Date of birth"], dayfirst=True, errors="coerce"
    )

    school_aged = (
        df["Date of birth"] + pd.DateOffset(years=5) < pd.to_datetime("today")
    ) & (df["Date of birth"] + pd.DateOffset(years=16) > pd.to_datetime("today"))

    no_schooling = (df["Main education establishment – URN"].isna()) & (
        df["Subsidiary education establishment – phase (dual registration)"].isna()
    )

    df_issues = df[school_aged & no_schooling]

    df_issues = df_issues.reset_index()

    link_id = tuple(
        zip(
            df_issues["Unique ID"],
            df_issues["Date of birth"],
            df_issues["Main education establishment – URN"],
            df_issues["Subsidiary education establishment – phase (dual registration)"],
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
        columns=[
            "Main education establishment – URN",
            "Subsidiary education establishment – phase (dual registration)",
        ],
        row_df=df_issues,
    )


def test_validate():
    fake_list = pd.DataFrame(
        [
            {
                "Unique ID": 0,
                "Date of birth": "01/01/2024",
                "Main education establishment – URN": pd.NA,
                "Subsidiary education establishment – phase (dual registration)": pd.NA,
            },  # passes
            {
                "Unique ID": 1,
                "Date of birth": "01/01/2010",
                "Main education establishment – URN": pd.NA,
                "Subsidiary education establishment – phase (dual registration)": "1",
            },  # passes
            {
                "Unique ID": 2,
                "Date of birth": "01/01/2010",
                "Main education establishment – URN": "1",
                "Subsidiary education establishment – phase (dual registration)": pd.NA,
            },  # passes
            {
                "Unique ID": 3,
                "Date of birth": "01/01/2010",
                "Main education establishment – URN": pd.NA,
                "Subsidiary education establishment – phase (dual registration)": pd.NA,
            },  # fails
        ]
    )

    result = run_rule(validate, {list_1: fake_list})

    issues = result.type1_issues

    issue_table = issues.table
    assert issue_table == list_1

    issue_columns = issues.columns
    assert issue_columns == [
        "Main education establishment – URN",
        "Subsidiary education establishment – phase (dual registration)",
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
                    pd.to_datetime("01/01/2010"),
                    pd.NA,
                    pd.NA,
                ),
                "ROW_ID": [3],
            }
        ]
    )

    assert issue_rows.equals(expected_df)

    assert result.definition.code == "108a"
    assert (
        result.definition.message
        == "School aged child/young person (5-16) without  main OR subsidiary education establishment"
    )