import jq
import pandas as pd


def transformer(file, rules):
    """
        assuming we have json file and transformation rules
        and we want to transform in into DataFrame format
        :file: JSON file
        :transformation_rules: dictionary based on
        jq library rules of transformation
    """

    jq_transformation_program = (".[] | "+str(rules)).replace("\n","")
    transformation = jq.compile(jq_transformation_program)

    new_data = transformation.input(file).all()
    df_from_json = pd.DataFrame.from_records(new_data)

    return df_from_json

