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
    code="109",
    module=SENTable.List_1,
    message="Duplicated UPN - return requires only the most recent initial EHCP date, close the first and submit the most recent.",
    affected_fields=["UNP"],
)
def validate(
    data_container: Mapping[SENTable, pd.DataFrame], rule_context: RuleContext
):
    df = data_container[list_1]
    df.index.name = "ROW_ID"

    # Each pupil <UPN> (N00001) must be unique across all pupils in the extract

    df = df[df["UPN"].notna()]
    df_issues = df[df.duplicated(subset=["UPN"], keep=False)].reset_index()

    link_id = tuple(
        zip(
            df_issues["Unique ID"],
            df_issues["UPN"],
        )
    )

    df_issues["ERROR_ID"] = link_id

    df_issues = (
        df_issues.groupby("ERROR_ID", group_keys=False)["ROW_ID"]
        .apply(list)
        .reset_index()
    )

    rule_context.push_type_1(table=list_1, columns=["UPN"], row_df=df_issues)


def test_validate():
    fake_list = pd.DataFrame(
        [
            {
                "Unique ID": "child1",
                "UPN": "1234",
            },
            {
                "Unique ID": "child2",
                "UPN": "1234",
            },
            {
                "Unique ID": "child3",
                "UPN": "12345",
            },
            {
                "Unique ID": "child4",
                "UPN": pd.NA,
            },
            {
                "Unique ID": "child4",
                "UPN": pd.NA,
            },
            {
                "Unique ID": "child5",
                "UPN": 1,
            },
            {
                "Unique ID": "child5",
                "UPN": 1,
            },
        ]
    )

    result = run_rule(validate, {list_1: fake_list})

    # The result contains a NamedTuple of issues encountered
    issues = result.type1_issues

    # get table name and check it. Replace ChildProtectionPlans with the name of your table.
    issue_table = issues.table
    assert issue_table == list_1

    # check that the right columns were returned. Replace CPPstartDate and CPPendDate with a list of your columns.
    issue_columns = issues.columns
    assert issue_columns == ["UPN"]

    # check that the location linking dataframe was formed properly.
    issue_rows = issues.row_df

    # replace 2 with the number of failing points you expect from the sample data.
    assert len(issue_rows) == 3
    # replace the table and column name as done earlier.
    # The last numbers represent the index values where you expect the sample data to fail the validation check.
    # check that the failing locations are contained in a DataFrame having the appropriate columns. These lines do not change.
    assert isinstance(issue_rows, pd.DataFrame)
    assert issue_rows.columns.to_list() == ["ERROR_ID", "ROW_ID"]

    # The ROW ID values represent the index positions where you expect the sample data to fail the validation check.
    expected_df = pd.DataFrame(
        [
            {
                "ERROR_ID": (
                    "child1",
                    "1234",
                ),
                "ROW_ID": [0],
            },
            {
                "ERROR_ID": (
                    "child2",
                    "1234",
                ),
                "ROW_ID": [1],
            },
            {
                "ERROR_ID": (
                    "child5",
                    1,
                ),
                "ROW_ID": [5, 6],
            },
        ]
    )

    assert issue_rows.equals(expected_df)

    # Check that the rule definition is what you wrote in the context above.

    # replace 8840 with the rule code and put the appropriate message in its place too.
    assert result.definition.code == "109"
    assert (
        result.definition.message
        == "Duplicated UPN - return requires only the most recent initial EHCP date, close the first and submit the most recent."
    )
