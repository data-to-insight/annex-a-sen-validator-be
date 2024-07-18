import datetime
import importlib
import json
from pathlib import Path

from sen_validator.utils import process_uploaded_files
from sen_validator.sen_validator import SenValidator

import click
import pytest


@click.group()
def cli():
    pass


@cli.command(name="ingress")
@click.option(
    "--filepath",
    "-f",
    default="/workspaces/annex-a-sen-validator-be/fake_data/fake_sen.xlsx",
)
def ingress(filepath):
    
    metadata = {"collectionYear": "2022", "localAuthority": "E09000027"}

    frontend_files_dict = {"This year": [filepath]}
    files_list = process_uploaded_files(frontend_files_dict)

    click.echo(files_list)

    v = SenValidator(files_list)


if __name__ == "__main__":
    cli()
