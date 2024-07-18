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
