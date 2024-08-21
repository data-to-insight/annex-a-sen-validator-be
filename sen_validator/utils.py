from io import TextIOWrapper

import pandas as pd

from sen_validator.types import UploadedFile, UploadError


def process_uploaded_files(input_files: dict[str, list]) -> list[UploadedFile]:
    """
    :param dict frontend_file_dict: dict of lists showing file content and the field into which user uploaded file.

    :return: files of UploadedFile type as ingress.read_from_text expects.
    """

    uploaded_files = []
    for field_name, file_refs in input_files.items():
        for file_ref in file_refs:
            # name attribute depends on whether on file type. CLI and API send different types.
            try:
                file_text = file_ref.read()
                filename = file_ref.filename
            except AttributeError:
                if isinstance(file_ref, TextIOWrapper):
                    # Text IO wrapper object from command line
                    filename = file_ref.name
                elif isinstance(file_ref, str):
                    # string path
                    filename = file_ref
                else:
                    raise UploadError("file format is not recognised.")

                with open(filename, "rb") as f:
                    file_text = f.read()

            uploaded_files.append(
                UploadedFile(
                    name=filename, description=field_name, file_content=file_text
                )
            )
    return uploaded_files


def create_issue_locs(issues):
    """
    Reverses grouping of issue rows, creating a DataFrame where each row contains a single issue location.

    :param NamedTuple-like-object issues: An object containing the fields for table, columns, and
        row_df for issues found when validating data.
    :returns: DataFrame with fields for ERROR_ID, ROW_ID, columns_affected, and tables_affected for
        issues found in validation.
    :rtype: DataFrame
    """

    # expand the row_id groups such that row_id value exists per row instead of a list
    df_issue_locs = issues.row_df
    df_issue_locs = df_issue_locs.explode("ROW_ID")

    # map every row_id to its respective columns_affected list and expand that list
    df_issue_locs["columns_affected"] = df_issue_locs["ERROR_ID"].apply(
        lambda x: issues.columns
    )
    df_issue_locs = df_issue_locs.explode("columns_affected")

    # all locations from a NamedTuple object will have the same singular value of tables_affected.
    df_issue_locs["tables_affected"] = str(issues.table)[9:]

    # now a one-to-one relationship exists across table-column-row
    df_issue_locs.reset_index(inplace=True)
    df_issue_locs.drop("index", axis=1, inplace=True)

    return df_issue_locs
