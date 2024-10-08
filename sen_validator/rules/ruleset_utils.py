import importlib
from typing import Iterable

from sen_validator.rule_engine import RuleDefinition, YearConfig


def check_duplicate_rules(new_funcs: dict, funcs_so_far: dict) -> None:
    duplicate_funcs = set(new_funcs.keys()) & set(funcs_so_far.keys())
    if duplicate_funcs:
        raise ValueError(f"Rule with code {duplicate_funcs} already exists")


def extract_validator_functions(
    file_paths: Iterable, marker: str = "__rule_def__"
) -> dict[str, RuleDefinition]:
    """
    :param list file_paths: list of file paths to extract functions from.
    :param str marker: marker to identify functions to extract.

    :return: functions extracted from files.
    :rtype: dict
    """
    validator_funcs: dict[str, RuleDefinition] = {}
    for path in file_paths:
        if path.stem == "__init__":
            continue
        try:
            rule_content = importlib.import_module(
                f"sen_validator.rules.{path.parent.stem}.{path.stem}"
            )
        except ModuleNotFoundError:
            # in the case where the file itself is passed in, rather than the directory
            rule_content = importlib.import_module(f"{path.stem}")

        validator_func = {
            str(element.__rule_def__.code): element.__rule_def__
            for _, element in vars(rule_content).items()
            if hasattr(element, "__rule_def__")
        }

        check_duplicate_rules(validator_func, validator_funcs)

        validator_funcs.update(validator_func)
    return validator_funcs


def update_validator_functions(
    prev_validator_funcs, this_year_config: YearConfig
) -> dict:
    """
    :param dict prev_registry: previous year's registry.
    :param dict this_year_config: codes of rules that have been added or deleted.

    :return: valid validator functions according to config.
    :rtype: dict
    """
    # Rules present in both will be updated to this year's version. rules present in only this year will be added.
    updated_validator_funcs = prev_validator_funcs | this_year_config.added_or_modified
    # delete rules by their rules codes, if specified.
    for deleted_rule in this_year_config.deleted:
        del updated_validator_funcs[deleted_rule]
    return updated_validator_funcs


def get_year_ruleset(validator_version: str) -> dict[str, RuleDefinition]:
    """
    Gets the registry of validation rules for the year specified in the metadata.
    """
    # for example, convert "0_0_1" to "sen_v0_0_1"
    ruleset = f"sen_v{validator_version}"

    module = importlib.import_module(f"sen_validator.rules.{ruleset}")
    registry = getattr(module, "registry")

    return registry
