

SEARCH_RULE = ".[] | "


def get_transformation_rules(rules: str, search_rule: str = SEARCH_RULE):
    return (search_rule + rules).replace("\n", "")