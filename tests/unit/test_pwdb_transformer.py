import json
from src.pwdb_transformer import transform_json_to_csv, get_transformation_rules


def test_transform_json_to_csv_number_of_columns_and_rows(tmpdir):
    JSON = [{'fieldData': {'title': 'Hardship case fund: Safety net for self-employed',
                           'title_nationalLanguage': 'hdadsa'}}]

    transformation = '''{
            "Title": .fieldData.title,
            "Title (national language)": .fieldData.title_nationalLanguage
            }'''

    file = tmpdir.join("test_JSON.json")
    file.write(json.dumps(JSON))

    transformation_rules = get_transformation_rules(transformation)
    # Compile tranformation
    df_transformed = transform_json_to_csv(file, transformation_rules)

    expected_list = ['Title', 'Title (national language)']

    df_rows = df_transformed.count()
    df_columns = df_transformed.columns

    # compare number of rows
    assert len(df_rows) == 2

    # compare number of columns
    assert len(df_columns) == len(expected_list)
    assert all([a == b for a, b in zip(df_columns, expected_list)])
