import json

import jq
import pandas as pd

SEARCH_RULE = ".[] | "


def get_transformation_rules(rules: str, search_rule: str = SEARCH_RULE):
    return (search_rule + rules).replace("\n", "")


def transform_json_to_csv(file: str, transformed_rules: str):
    """
        assuming we have json file and transformation rules
        and we want to transform in into DataFrame format
        :file: JSON file address
        :transformation_rules: dictionary based on
        jq library rules of transformation
    """

    with open(file) as file:
        content = file.read()
        data = json.loads(content)

    transformation = jq.compile(transformed_rules)

    new_data = transformation.input(data).all()
    df_from_json = pd.DataFrame.from_records(new_data)

    return df_from_json

