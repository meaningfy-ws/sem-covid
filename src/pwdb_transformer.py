import json

import jq
import pandas as pd


def transform_json_to_csv(file: list, rules: str):
    """
        assuming we have json file and transformation rules
        and we want to transform in into DataFrame format
        :file_content: JSON file
        :transformation_rules: dictionary based on
        jq library rules of transformation
    """

    with open(file) as file:
        content = file.read()
        data = json.loads(content)

    jq_transformation_program = (".[] | "+str(rules)).replace("\n", "")
    transformation = jq.compile(jq_transformation_program)

    new_data = transformation.input(data).all()
    df_from_json = pd.DataFrame.from_records(new_data)

    return df_from_json

