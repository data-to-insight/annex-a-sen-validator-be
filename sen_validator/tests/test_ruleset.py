from sen_validator.rules.ruleset_utils import get_year_ruleset


def test_ruleset_complete():
    registry = get_year_ruleset("0_0_1")
    # TODO finish this properly
    # check that the current version of SEN rules pulls in all the rules.
    assert len(registry) == len(registry)
