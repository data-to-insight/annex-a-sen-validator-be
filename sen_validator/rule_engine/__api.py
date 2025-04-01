import importlib
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, Optional


class SENTable(Enum):
    """
    An enumeration class (https://docs.python.org/3/library/enum.html).
    Used in validation to select SEN data modules/tables and fields/columns
    and assign them to variables. For practical reasons, this is done to
    ensure consistent spelling.
    """
    List_1 = Enum(
        "List_1",
        [
            "Unique ID",
            "UPN",
            "ULN",
            "Date of birth",
            "Gender",
            "Ethnicity",
            "Date initial EHC plan issued",
            "Date updated EHC plan issued",
            "Date EHC plan last reviewed",
            "SEN primary need",
            "Main education establishment – URN",
            "Main education establishment – phase",
            "Subsidiary education establishment – phase (dual registration)",
            "Elective home education",
            "Suspensions",
            "Permanent exclusions",
            "Absence",
            "Pupil Premium",
            "Known to children's social care?",
            "Which children's social care team?",
            "Does the child or young person have a disability?",
        ],
    )

    List_2 = Enum(
        "List_2",
        [
            "Unique ID",
            "UPN",
            "ULN",
            "Date of birth",
            "Gender",
            "Ethnicity",
            "SEN primary need",
            "Main education establishment – URN",
            "Main education establishment – phase",
            "Subsidiary education establishment – phase (dual registration)",
            "Suspensions",
            "Permanent exclusions",
            "Absence",
            "Pupil Premium",
            "Known to children's social care?",
            "Which children's social care team?",
            "Does the child or young person have a disability?",
        ],
    )

    def __getattr__(self, item):
        """
        Used to get attributes within the SENtable class. Practically used to define
        fields/column variables from within tables for use in validation rules.

        :param variable item: The name of a module and field to be used for
            a validation rule.
        :returns: A variable containing a field/column for validation, or an error
            (generally on misspelling).
        :rtype: Variable, error.
        """

        if not item.startswith("_"):
            try:
                return self.value[item].name
            except KeyError as kerr:
                raise AttributeError(f"Table {self.name} has no field {item}") from kerr
        else:
            return super().__getattr__(item)


class RuleType(Enum):
    """
    An enumeration type class that defines available rule types.
    Used to assign 'Error' or 'Query' to each rule in validation.
    """

    ERROR = "Error"
    QUERY = "Query"


@dataclass(frozen=True, eq=True)
class RuleDefinition:
    """
    A dataclass type class used in each validation to assign information about
    each validation rule to the rule.

    :param int code: The rule code for each rule.
    :param function func: Used to import the validation rule function.
    :param RuleType-class rule_type: A RuleType class object accepts a string denoting if
        the rule is an error or a query.
    :param CINtable-object module: Accepts a string denoting the module/table affected by a
        validation rule.
    :param str affected_fields: The fields/columns affected by a validation rule.
    :param str message: The message to be displayed if rule is flagged.
    :returns: RuleDefinition object containing information about validation rules.
    :rtype: dataclass object.
    """

    code: str
    func: Callable
    rule_type: RuleType = RuleType.ERROR
    module: Optional[SENTable] = None
    affected_fields: Optional[Iterable[str]] = None
    message: Optional[str] = None


@dataclass(eq=True)
class YearConfig:
    deleted: list[str]
    added_or_modified: dict[str, RuleDefinition]
