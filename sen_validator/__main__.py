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


@cli.command(name="run")
@click.option(
    "--filepath",
    "-f",
    default="/workspaces/annex-a-sen-validator-be/fake_data/fake_sen.xlsx",
)
def ingress(filepath):
    ruleset = "sen_v0_0_1"

    # metadata = {"collectionYear": "2022", "localAuthority": "E09000027"}

    frontend_files_dict = {"This year": [filepath]}
    files_list = process_uploaded_files(frontend_files_dict)

    module = importlib.import_module(f"sen_validator.rules.{ruleset}")
    ruleset_registry = getattr(module, "registry")

    # click.echo(ruleset_registry)

    v = SenValidator(files_list, ruleset_registry)

    full_issue_df = v.full_issue_df

    click.echo(full_issue_df)


@cli.command(name="test")
@click.argument("rule", required=False)
@click.option(
    "--ruleset",
    "-r",
    default="sen_v0_0_1",
    help="Which ruleset to use, e.g. sen_v0_0_1",
)
def test_cmd(rule, ruleset):
    """
    Test all (or individual) rules in a ruleset. Note: tests the code
    for the rule, this is not used for validating data.

    Allows use of the CLI to test a ruleset or individual rules against the
    pytest written in each of their files. Useful for bugfixing. Defaults
    to the cin2022_23 ruleset.

    Can be called to test all rules using:
    python -m cin_validator test
    To test individual rules:
    python -m cin_validator <rulecode>
    For example:
    python -m cin_validator test 8875

    :param str rule: Used to specify an individual rule to test.
    :param str ruleset: Use to give the name of a set of validation rules to test
        (defaults to cin2022_23).
    :returns: Pytest output in terminal of rules passing and failing.
    :rtype: Pytest output in terminal.
    """

    module = importlib.import_module(f"sen_validator.rules.{ruleset}")
    module_folder = Path(module.__file__).parent

    ruleset_registry = getattr(module, "registry")

    if rule:
        rule = str(rule)
        # when rule code is specified, test specific rule.
        rule_def = ruleset_registry.get(rule)
        if not rule_def:
            # if the get returns a <NoneType>
            click.secho(f"Rule {rule} not found.", err=True, fg="red")
            return 1
        test_files = [os.path.join(module_folder, f"rule_{rule}.py")]
    else:
        # else test all rules.
        test_files = [
            str(p.absolute())
            for p in module_folder.glob("*.py")
            if p.stem != "__init__"
        ]

    pytest.main(test_files)


if __name__ == "__main__":
    cli()
