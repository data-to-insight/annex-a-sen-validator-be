import logging
from io import BytesIO
from pathlib import Path
from typing import Dict, Iterator, List, Tuple, Union

import pandas as pd
from numpy import nan
from pandas import DataFrame

import collections.abc

from sen_validator.config import column_names
from sen_validator.types import UploadedFile, UploadError

logger = logging.getLogger(__name__)


class _BufferedUploadedFile(collections.abc.Mapping):
    def __init__(self, file, name, description):
        self.name = name
        self.description = description
        self.file = Path(file)
        if not self.file.is_file():
            raise FileNotFoundError(f"{self.file} not found.")

    def __getitem__(self, k):
        if k == "name":
            return self.name
        elif k == "description":
            return self.description
        elif k == "file_content":
            with open(self.file, "rb") as file:
                return file.read()
        else:
            raise AttributeError(f"{k} not found")

    def __len__(self) -> int:
        return 3

    def __iter__(self) -> Iterator:
        pass


def read_from_text(
    raw_files: List[UploadedFile],
) -> Tuple[Dict[str, DataFrame], Dict[str, Union[str, DataFrame]]]:
    """
    Reads from a raw list of files passed from javascript. These files are of
    the form e.g.
    [
        {name: 'filename.csv', file_content: <file contents>, description: <upload metadata>}
    ]

    This function will try to catch most basic upload errors, and dispatch other errors
    to either the csv or xml reader based on the file extension.
    """
    logger.info(f"Reading from text.")
    metadata_extras = {}

    raw_files = [f for f in raw_files]


    extensions = list(set([f["name"].split(".")[-1].lower() for f in raw_files]))

    if len(raw_files) == 0:
        raise UploadError("No AnnexA SEN data uploaded")
    elif len(extensions) > 1:
        raise UploadError(
            f"Mix of CSV and XLSX files found ({extensions})! Please reupload the correct files."
        )
    else:
        if extensions == ["csv"]:
            metadata_extras["file_format"] = "csv"
            raise UploadError(f"CSVs uploaded, expected XLSX files.")
        elif extensions == ["xlsx"]:
            metadata_extras["file_format"] = "xlsx"
            return read_xlsx_from_text(raw_files[0]["file_content"]), metadata_extras
        else:
            raise UploadError(f"Unknown file type {extensions[0]} found.")


def read_files(files: Union[str, Path]) -> List[UploadedFile]:
    uploaded_files: List[_BufferedUploadedFile] = []
    for filename in files:
        uploaded_files.append(
            _BufferedUploadedFile(file=filename, name=filename, description="This year")
        )
    return uploaded_files


def capitalise_object_dtype_cols(df) -> pd.DataFrame:
    """This function takes in a pandas dataframe and capitalizes all the strings found in it."""
    for col in df.select_dtypes(include="object"):
        df[col] = df[col].str.upper()
    return df


def all_cols_to_object_dtype(df) -> pd.DataFrame:
    """This function converts all columns to object dtype."""
    for col in df.columns:
        if df.dtypes[col] != object:
            df[col] = df[col].values.astype(object)
    return df


def read_xlsx_from_text(raw_files: List[UploadedFile]) -> Dict[str, DataFrame]:
    # def _get_file_type(df) -> str:
    #     for table_name, expected_columns in column_names.items():
    #         if set(df.columns) == set(expected_columns):
    #             logger.info(f"Loaded {table_name} from xlsx. ({len(df)} rows)")
    #             return table_name
    #     else:
    #         raise UploadError(
    #             f"Failed to match provided data ({list(df.columns)}) to known column names!"
    #         )


    xlsx_file = BytesIO(raw_files)
    try:
        max_cols = max([len(cols) for cols in column_names.values()])
        dfs = pd.read_excel(
            xlsx_file,
            converters={
                i: lambda s: str(s) if s != "" else nan for i in range(max_cols)
            },
            sheet_name=None,
        )
    except UnicodeDecodeError:
        # raw_files is a list of files of type UploadedFile(TypedDict) whose instance is a dictionary containing the fields name, file_content, Description.
        # TODO: attempt to identify files that couldnt be decoded at this point; continue; then raise the exception outside the for loop, naming the uploaded filenames
        raise UploadError(
            f"Failed to decode one or more files. Try opening the text "
            f"file(s) in Notepad, then 'Saving As...' with the UTF-8 encoding"
        )
        # arrange column data types
    for list_no, df in dfs.items():
        logger.debug("+" * 50)
        logger.debug("DF DATATYPES BEFORE CONVERSION", df.dtypes)
        df = all_cols_to_object_dtype(df)
        logger.debug("AFTER CONVERSION BEFORE CAPITALISING", df.dtypes)
        # capitalize all string input
        df = capitalise_object_dtype_cols(df)
        logger.debug("DF DATATYPES AFTER CAPITALISING", df.dtypes)

        dfs[list_no] = df

    return dfs
