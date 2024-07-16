from pathlib import Path

files = Path(__file__).parent.glob("*.py")
registry = extract_validator_functions(files)

__all__ = ["registry"]
