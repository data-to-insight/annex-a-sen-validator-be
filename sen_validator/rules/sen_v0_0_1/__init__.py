from pathlib import Path
from sen_validator.rule_engine import RuleDefinition, YearConfig, RuleContext

from sen_validator.rules.ruleset_utils import (
    extract_validator_functions,
    update_validator_functions,
)

files = Path(__file__).parent.glob("*.py")

registry = extract_validator_functions(files)
__all__ = ["registry"]
